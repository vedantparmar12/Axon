"""
HiRAG Provider for MCP RAG Integration
Provides hierarchical RAG capabilities with advanced entity extraction and clustering.
"""
import asyncio
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

from hirag.hirag import HiRAG
from hirag.base import QueryParam
from hirag._storage import JsonKVStorage, NanoVectorDBStorage, NetworkXStorage


class HiRAGProvider:
    """Provider for hierarchical RAG operations using hiRAG framework."""

    def __init__(self, working_dir: str = None):
        """Initialize hiRAG provider with configuration from environment."""
        self.working_dir = working_dir or f"./hirag_cache"
        self.chunk_size = int(os.getenv("HIRAG_CHUNK_SIZE", "1200"))
        self.chunk_overlap = int(os.getenv("HIRAG_CHUNK_OVERLAP", "100"))
        self.max_clusters = int(os.getenv("HIRAG_MAX_CLUSTERS", "10"))
        self.enable_cache = os.getenv("HIRAG_ENABLE_CACHE", "true").lower() == "true"
        self.mode = os.getenv("HIRAG_MODE", "hi")

        # Initialize hiRAG instance
        self.hirag = HiRAG(
            working_dir=self.working_dir,
            enable_hierachical_mode=True,
            enable_local=True,
            enable_naive_rag=(self.mode == "naive"),
            chunk_token_size=self.chunk_size,
            chunk_overlap_token_size=self.chunk_overlap,
            max_graph_cluster_size=self.max_clusters,
        )

        # Initialize storages
        self._init_storages()

    def _init_storages(self):
        """Initialize storage backends for hiRAG."""
        self.kv_storage = JsonKVStorage(namespace="hirag_kv", global_config={"working_dir": self.working_dir})
        self.vector_storage = NanoVectorDBStorage(namespace="hirag_vector", global_config={"working_dir": self.working_dir})
        self.graph_storage = NetworkXStorage(namespace="hirag_graph", global_config={"working_dir": self.working_dir})

    async def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        Add documents to the hiRAG system with hierarchical processing.

        Args:
            documents: List of documents with 'content', 'metadata', and 'id' fields
        """
        try:
            # Convert documents to hiRAG format
            doc_texts = {}
            for doc in documents:
                doc_texts[doc['id']] = doc['content']

            # Process documents through hiRAG pipeline
            await self.hirag.ainsert(doc_texts)

        except Exception as e:
            print(f"Error adding documents to hiRAG: {e}")
            raise

    async def search(self, query: str, top_k: int = 10, mode: str = None) -> List[Dict[str, Any]]:
        """
        Search using hierarchical RAG with entity-aware retrieval.

        Args:
            query: Search query
            top_k: Number of results to return
            mode: Search mode (hi, hi_global, hi_local, hi_bridge, hi_nobridge, naive)

        Returns:
            List of relevant documents with scores and context
        """
        try:
            search_mode = mode or self.mode

            # Create query parameters
            query_param = QueryParam(
                mode=search_mode,
                top_k=top_k,
                top_m=min(top_k // 2, 5),  # Retrieved entities per community
                only_need_context=False,
                response_type="Multiple Paragraphs",
                level=2,  # Hierarchy level
            )

            # Perform hierarchical search
            response = await self.hirag.aquery(query, param=query_param)

            # Format results
            results = []
            if hasattr(response, 'context') and response.context:
                # Extract context and format as results
                context_parts = response.context.split('\n\n')
                for i, part in enumerate(context_parts):
                    if part.strip():
                        results.append({
                            'content': part.strip(),
                            'metadata': {
                                'source': 'hirag',
                                'mode': search_mode,
                                'rank': i + 1,
                                'type': 'hierarchical_context'
                            },
                            'score': 1.0 - (i * 0.1),  # Decreasing relevance
                        })
            else:
                # Fallback: use response directly
                results.append({
                    'content': str(response),
                    'metadata': {
                        'source': 'hirag',
                        'mode': search_mode,
                        'type': 'direct_response'
                    },
                    'score': 1.0,
                })

            return results[:top_k]

        except Exception as e:
            print(f"Error in hiRAG search: {e}")
            return []

    async def get_entity_graph(self, query: str = None) -> Dict[str, Any]:
        """
        Get the entity graph structure for visualization or analysis.

        Args:
            query: Optional query to filter entities

        Returns:
            Graph structure with nodes and edges
        """
        try:
            # Get graph data from storage
            graph_data = await self.graph_storage.get_network_x_graph()

            if graph_data is None:
                return {"nodes": [], "edges": []}

            # Convert to serializable format
            nodes = []
            edges = []

            for node in graph_data.nodes(data=True):
                nodes.append({
                    'id': node[0],
                    'label': node[0],
                    'data': node[1]
                })

            for edge in graph_data.edges(data=True):
                edges.append({
                    'source': edge[0],
                    'target': edge[1],
                    'data': edge[2]
                })

            return {
                'nodes': nodes,
                'edges': edges,
                'node_count': len(nodes),
                'edge_count': len(edges)
            }

        except Exception as e:
            print(f"Error getting entity graph: {e}")
            return {"nodes": [], "edges": []}

    async def get_communities(self) -> List[Dict[str, Any]]:
        """
        Get the detected communities from the entity graph.

        Returns:
            List of communities with their members and reports
        """
        try:
            communities = []

            # Get community data from storage
            community_data = await self.kv_storage.get_by_ids(["communities"])

            if community_data and "communities" in community_data:
                for community in community_data["communities"]:
                    communities.append({
                        'id': community.get('title', 'Unknown'),
                        'title': community.get('title', 'Unknown Community'),
                        'summary': community.get('report_string', ''),
                        'nodes': community.get('nodes', []),
                        'edges': community.get('edges', []),
                        'level': community.get('level', 0),
                        'occurrence': community.get('occurrence', 0.0),
                    })

            return communities

        except Exception as e:
            print(f"Error getting communities: {e}")
            return []

    async def clear_cache(self):
        """Clear all cached data and reinitialize storages."""
        try:
            # Clear all storages
            await self.kv_storage.clear_namespace()
            await self.vector_storage.clear_namespace()
            await self.graph_storage.clear_namespace()

            # Reinitialize
            self._init_storages()

        except Exception as e:
            print(f"Error clearing hiRAG cache: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the hiRAG system."""
        return {
            'working_dir': self.working_dir,
            'chunk_size': self.chunk_size,
            'chunk_overlap': self.chunk_overlap,
            'max_clusters': self.max_clusters,
            'mode': self.mode,
            'enable_cache': self.enable_cache,
        }