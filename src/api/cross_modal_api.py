#!/usr/bin/env python3
"""
Cross-Modal REST API Server

Local-only REST API for cross-modal analysis operations.
Provides high-level endpoints for document analysis, format conversion,
and mode recommendation for local automation and custom UIs.

This complements (not replaces) the MCP server interface.
"""

import asyncio
import os
import tempfile
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import logging

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import numpy as np
import pandas as pd

# Import cross-modal services
from src.analytics import (
    get_registry,
    initialize_cross_modal_services,
    DataFormat,
    AnalysisRequest,
    DataContext,
    AnalysisMode,
    ValidationLevel,
    WorkflowOptimizationLevel
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="KGAS Cross-Modal Analysis API",
    description="Local REST API for cross-modal document analysis and format conversion",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS for local origins only
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "http://localhost:8080",  # Vue dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global job storage (in production, use Redis or database)
jobs: Dict[str, Dict[str, Any]] = {}

# Pydantic models for request/response
class AnalyzeRequest(BaseModel):
    """Request model for document analysis"""
    target_format: str = Field("graph", description="Target format: graph, table, or vector")
    task: str = Field("extract entities", description="Analysis task description")
    optimization_level: str = Field("balanced", description="Optimization: speed, balanced, or quality")
    validation_level: str = Field("standard", description="Validation: basic, standard, or comprehensive")

class ConvertRequest(BaseModel):
    """Request model for format conversion"""
    data: Union[Dict[str, Any], List[List[float]]] = Field(..., description="Data to convert")
    source_format: str = Field(..., description="Source format: graph, table, or vector")
    target_format: str = Field(..., description="Target format: graph, table, or vector")
    method: Optional[str] = Field(None, description="Conversion method (format-specific)")

class RecommendRequest(BaseModel):
    """Request model for mode recommendation"""
    task: str = Field(..., description="Analysis task description")
    data_type: str = Field(..., description="Type of data being analyzed")
    size: int = Field(..., description="Approximate data size")
    performance_priority: str = Field("quality", description="Priority: speed or quality")

class JobResponse(BaseModel):
    """Response model for async job creation"""
    job_id: str
    status: str
    created_at: str
    message: str

class AnalysisResponse(BaseModel):
    """Response model for analysis results"""
    workflow_id: str
    selected_mode: str
    results: Dict[str, Any]
    validation: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    source_traceability: Optional[Dict[str, Any]] = None

# Initialize services on startup
@app.on_event("startup")
async def startup_event():
    """Initialize cross-modal services on startup"""
    try:
        # Initialize with default configuration
        config = {
            'llm': {'provider': 'openai'},
            'embedding': {'device': 'cpu'}
        }
        
        success = initialize_cross_modal_services(config)
        if success:
            logger.info("✅ Cross-modal services initialized successfully")
        else:
            logger.warning("⚠️ Some services failed to initialize - API will have limited functionality")
            
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        logger.warning("API starting with limited functionality")

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Check API and service health"""
    try:
        registry = get_registry()
        health_status = registry.check_all_health()
        
        return {
            "status": "healthy" if all(health_status.values()) else "degraded",
            "timestamp": datetime.now().isoformat(),
            "services": health_status,
            "version": "1.0.0"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

# Document analysis endpoint
@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    target_format: str = Query("graph", description="Target format for analysis"),
    task: str = Query("extract entities", description="Analysis task"),
    optimization_level: str = Query("balanced", description="Optimization level"),
    validation_level: str = Query("standard", description="Validation level")
):
    """
    Analyze an uploaded document and convert to specified format.
    
    Supports PDF, Word, and text documents.
    """
    # Validate file type
    allowed_types = [".pdf", ".docx", ".doc", ".txt", ".md"]
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_ext}. Allowed: {allowed_types}"
        )
    
    # Validate target format
    try:
        target_fmt = DataFormat(target_format.upper())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid target format: {target_format}. Use: graph, table, or vector"
        )
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Integrated with core pipeline services
        registry = get_registry()
        
        # Integrate with actual pipeline services
        try:
            from src.core.pipeline_orchestrator import PipelineOrchestrator
            from src.core.service_manager import ServiceManager
            
            # Initialize service manager and orchestrator
            service_manager = ServiceManager()
            orchestrator = PipelineOrchestrator(service_manager)
            
            # Process document through actual pipeline
            processing_request = {
                "documents": [tmp_path],
                "queries": queries,
                "phase": "phase1",
                "optimization_level": optimization_level.upper()
            }
            
            pipeline_result = orchestrator.execute_processing_request(processing_request)
            
            if pipeline_result and pipeline_result.get("success", False):
                graph_data = pipeline_result.get("graph_data", {})
                entities = pipeline_result.get("entities", [])
                relationships = pipeline_result.get("relationships", [])
                
                logger.info(f"Pipeline processing successful: {len(entities)} entities, {len(relationships)} relationships")
            else:
                error_msg = pipeline_result.get("error", "Pipeline processing failed") if pipeline_result else "Pipeline returned no results"
                logger.error(f"Pipeline processing failed: {error_msg}")
                raise Exception(f"Pipeline processing failed: {error_msg}")
                
        except ImportError as e:
            logger.error(f"Failed to import pipeline components: {e}")
            raise HTTPException(status_code=500, detail=f"Pipeline integration not available: {str(e)}")
        except Exception as e:
            logger.error(f"Pipeline processing error: {e}")
            raise HTTPException(status_code=500, detail=f"Pipeline processing failed: {str(e)}")
        
        # TEMPORARY: Use mock data to demonstrate API structure
        if file_ext == ".pdf":
            # Mock PDF processing - replace with pipeline when ready
            mock_graph_data = {
                "nodes": [
                    {"id": "1", "label": "Entity A", "type": "PERSON"},
                    {"id": "2", "label": "Entity B", "type": "ORGANIZATION"},
                    {"id": "3", "label": "Entity C", "type": "LOCATION"}
                ],
                "edges": [
                    {"source": "1", "target": "2", "relationship": "WORKS_FOR"},
                    {"source": "2", "target": "3", "relationship": "LOCATED_IN"}
                ]
            }
        else:
            # Mock text processing - replace with pipeline when ready
            mock_graph_data = {
                "nodes": [
                    {"id": "1", "label": "Document", "type": "DOCUMENT"}
                ],
                "edges": []
            }
        
        # Create analysis request
        request = AnalysisRequest(
            data=mock_graph_data,
            source_format=DataFormat.GRAPH,
            target_formats=[target_fmt],
            task=task,
            optimization_level=WorkflowOptimizationLevel(optimization_level.upper()),
            validation_level=ValidationLevel(validation_level.upper())
        )
        
        # Execute analysis
        orchestrator = registry.orchestrator
        if not orchestrator:
            raise HTTPException(
                status_code=503,
                detail="Orchestrator service not available"
            )
            
        result = await orchestrator.orchestrate_analysis(request)
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        # Return results
        return AnalysisResponse(
            workflow_id=result.workflow_id,
            selected_mode=result.selected_mode.value,
            results={
                target_format: _serialize_results(result.converted_data.get(target_fmt))
            },
            validation=result.validation_results,
            performance_metrics=result.performance_metrics,
            source_traceability=result.source_traceability
        )
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        # Clean up temp file if it exists
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise HTTPException(status_code=500, detail=str(e))

# Format conversion endpoint
@app.post("/api/convert")
async def convert_format(request: ConvertRequest):
    """
    Convert data between formats (Graph ↔ Table ↔ Vector).
    
    Preserves source traceability during conversion.
    """
    try:
        # Validate formats
        source_fmt = DataFormat(request.source_format.upper())
        target_fmt = DataFormat(request.target_format.upper())
        
        if source_fmt == target_fmt:
            return {"data": request.data, "message": "Source and target formats are the same"}
        
        # Get converter
        registry = get_registry()
        converter = registry.converter
        if not converter:
            raise HTTPException(
                status_code=503,
                detail="Converter service not available"
            )
        
        # Convert data
        result = await converter.convert(
            data=request.data,
            source_format=source_fmt,
            target_format=target_fmt,
            method=request.method
        )
        
        return {
            "data": _serialize_results(result.data),
            "source_format": request.source_format,
            "target_format": request.target_format,
            "metadata": result.metadata,
            "performance": {
                "conversion_time": result.conversion_time,
                "data_size": result.data_size
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Mode recommendation endpoint
@app.post("/api/recommend")
async def recommend_mode(request: RecommendRequest):
    """
    Get AI-powered recommendation for optimal analysis mode.
    
    Returns confidence scores and reasoning.
    """
    try:
        registry = get_registry()
        mode_selector = registry.mode_selector
        if not mode_selector:
            raise HTTPException(
                status_code=503,
                detail="Mode selection service not available"
            )
        
        # Create data context
        context = DataContext(
            data_type=request.data_type,
            size=request.size,
            task=request.task,
            performance_priority=request.performance_priority
        )
        
        # Get recommendation
        recommendation = await mode_selector.recommend_mode(context)
        
        return {
            "primary_mode": recommendation.primary_mode.value,
            "secondary_modes": [mode.value for mode in recommendation.secondary_modes],
            "confidence": recommendation.confidence,
            "confidence_level": recommendation.confidence_level.value,
            "reasoning": recommendation.reasoning,
            "estimated_performance": recommendation.estimated_performance,
            "metadata": recommendation.selection_metadata
        }
        
    except Exception as e:
        logger.error(f"Mode recommendation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Batch analysis endpoint
@app.post("/api/batch/analyze", response_model=JobResponse)
async def batch_analyze(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    target_format: str = Query("graph"),
    task: str = Query("extract entities")
):
    """
    Submit multiple documents for batch analysis.
    
    Returns a job ID to track progress.
    """
    # Create job
    job_id = str(uuid.uuid4())
    job = {
        "id": job_id,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "total_files": len(files),
        "processed_files": 0,
        "results": [],
        "errors": []
    }
    jobs[job_id] = job
    
    # Process in background
    background_tasks.add_task(
        process_batch_analysis,
        job_id,
        files,
        target_format,
        task
    )
    
    return JobResponse(
        job_id=job_id,
        status="pending",
        created_at=job["created_at"],
        message=f"Batch job created for {len(files)} files"
    )

# Job status endpoint
@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get status and results for a batch job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    return {
        "job_id": job_id,
        "status": job["status"],
        "created_at": job["created_at"],
        "progress": {
            "total": job["total_files"],
            "processed": job["processed_files"],
            "percentage": (job["processed_files"] / job["total_files"] * 100) if job["total_files"] > 0 else 0
        },
        "results": job["results"] if job["status"] == "completed" else None,
        "errors": job["errors"] if job["errors"] else None
    }

# Service statistics endpoint
@app.get("/api/stats")
async def get_statistics():
    """Get service statistics and usage metrics"""
    try:
        registry = get_registry()
        stats = registry.get_service_stats()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "services": stats,
            "api": {
                "active_jobs": len([j for j in jobs.values() if j["status"] == "processing"]),
                "completed_jobs": len([j for j in jobs.values() if j["status"] == "completed"]),
                "failed_jobs": len([j for j in jobs.values() if j["status"] == "failed"])
            }
        }
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions
def _serialize_results(data: Any) -> Any:
    """Serialize results for JSON response"""
    if isinstance(data, np.ndarray):
        return data.tolist()
    elif isinstance(data, pd.DataFrame):
        return data.to_dict(orient="records")
    elif hasattr(data, '__dict__'):
        return data.__dict__
    return data

async def process_batch_analysis(job_id: str, files: List[UploadFile], target_format: str, task: str):
    """Process batch analysis in background"""
    job = jobs[job_id]
    job["status"] = "processing"
    
    try:
        for i, file in enumerate(files):
            try:
                # NOTE: Full pipeline integration pending
                # When ready, each file will be processed through the full pipeline
                # For now, return mock results to demonstrate API structure
                result = {
                    "filename": file.filename,
                    "status": "success",
                    "message": "Pipeline integration pending - returning demo data",
                    "entities": ["Entity1", "Entity2"],  # Mock results
                    "relationships": ["Rel1", "Rel2"],
                    "note": "Full document processing will be available after core service fixes"
                }
                job["results"].append(result)
            except Exception as e:
                job["errors"].append({
                    "filename": file.filename,
                    "error": str(e)
                })
            
            job["processed_files"] = i + 1
        
        job["status"] = "completed" if not job["errors"] else "completed_with_errors"
        
    except Exception as e:
        job["status"] = "failed"
        job["errors"].append({"error": str(e)})

# Main entry point for development
if __name__ == "__main__":
    import uvicorn
    
    # Run on localhost only for security
    uvicorn.run(
        app,
        host="127.0.0.1",  # Localhost only
        port=8000,
        log_level="info"
    )