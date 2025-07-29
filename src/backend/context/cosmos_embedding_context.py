# src/backend/context/cosmos_embedding_context.py
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
import json
import logging
from semantic_kernel.text import text_embedding_generation
from context.cosmos_memory_kernel import CosmosMemoryContext

logger = logging.getLogger(__name__)

class CosmosEmbeddingContext(CosmosMemoryContext):
    """Extended Cosmos context with embedding support for WAF guidance."""
    
    def __init__(self, *args, embedding_generator=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.embedding_generator = embedding_generator
        
    async def store_waf_guidance(
        self, 
        resource_type: str,
        pillar: str,
        guidance_text: str,
        source_url: str,
        metadata: Dict = None
    ) -> str:
        """Store WAF guidance with embeddings."""
        
        # Generate embedding for the guidance
        embedding = None
        if self.embedding_generator:
            try:
                embedding_result = await self.embedding_generator.generate_embeddings_async([guidance_text])
                embedding = embedding_result[0] if embedding_result else None
            except Exception as e:
                logger.error(f"Failed to generate embedding: {e}")
        
        document = {
            "id": f"{resource_type}_{pillar}_{hash(guidance_text)}",
            "session_id": self.session_id,
            "user_id": self.user_id,
            "data_type": "waf_guidance",
            "resource_type": resource_type,
            "pillar": pillar,
            "guidance_text": guidance_text,
            "embedding": embedding.tolist() if embedding is not None else None,
            "source_url": source_url,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat()
        }
        
        await self._container.upsert_item(body=document)
        logger.info(f"Stored WAF guidance for {resource_type} - {pillar}")
        
        return document["id"]
    
    async def find_relevant_guidance(
        self,
        resource_config: Dict,
        resource_type: str,
        pillars: List[str] = None,
        top_k: int = 10
    ) -> List[Dict]:
        """Find relevant WAF guidance using text search (simplified without vector search)."""
        
        await self.ensure_initialized()
        
        # Simple text-based query for now
        query = """
        SELECT TOP @top_k
            c.id,
            c.resource_type,
            c.pillar,
            c.guidance_text,
            c.source_url,
            c.metadata
        FROM c
        WHERE c.data_type = 'waf_guidance'
        AND c.resource_type = @resource_type
        """
        
        parameters = [
            {"name": "@top_k", "value": top_k},
            {"name": "@resource_type", "value": resource_type}
        ]
        
        if pillars:
            query += " AND c.pillar IN (" + ",".join([f"'{p}'" for p in pillars]) + ")"
        
        try:
            items = self._container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            )
            
            results = []
            async for item in items:
                results.append(item)
            
            return results
        except Exception as e:
            logger.error(f"Failed to find relevant guidance: {e}")
            return []
    
    async def get_cached_assessment(
        self,
        resource_id: str,
        cache_duration_hours: int = 24
    ) -> Optional[Dict]:
        """Get cached assessment if available and fresh."""
        
        try:
            cutoff_time = (datetime.utcnow() - timedelta(hours=cache_duration_hours)).isoformat()
            
            query = """
            SELECT TOP 1 * FROM c 
            WHERE c.resource_id = @resource_id 
            AND c.data_type = 'assessment_cache'
            AND c.assessment_time > @cutoff_time
            ORDER BY c.assessment_time DESC
            """
            
            parameters = [
                {"name": "@resource_id", "value": resource_id},
                {"name": "@cutoff_time", "value": cutoff_time}
            ]
            
            items = self._container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            )
            
            async for item in items:
                return item
                
            return None
            
        except Exception as e:
            logger.error(f"Failed to get cached assessment: {e}")
            return None
    
    async def cache_assessment(
        self,
        resource_id: str,
        findings: List[Dict],
        scores: Dict[str, float]
    ):
        """Cache assessment results."""
        
        document = {
            "id": f"assessment_{resource_id}_{datetime.utcnow().timestamp()}",
            "session_id": self.session_id,
            "user_id": self.user_id,
            "data_type": "assessment_cache",
            "resource_id": resource_id,
            "findings": findings,
            "scores": scores,
            "assessment_time": datetime.utcnow().isoformat()
        }
        
        await self._container.upsert_item(body=document)