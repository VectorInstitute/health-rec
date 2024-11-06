'use client';

import React from 'react';
import ReactFlow, {
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  Panel,
  MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';

const ArchitectureDiagram: React.FC = () => {
  const nodes: Node[] = [
    {
      id: 'user',
      data: { label: 'User' },
      position: { x: 200, y: 0 },
      style: { background: '#f0f0f0', border: '2px solid #000' },
    },
    {
      id: 'frontend',
      data: { label: 'Frontend (Next.js)' },
      position: { x: -100, y: 100 },
      style: { background: '#e6f3ff', width: 200, border: '2px dashed #666' },
    },
    {
        id: 'mapbox',
        data: { label: 'Mapbox API' },
        position: { x: -120, y: 200 },
        style: { background: '#ffffff', width: 200, border: '2px dashed #666' },
      },
      {
        id: 'google maps',
        data: { label: 'Google Maps API' },
        position: { x: -120, y: 0 },
        style: { background: '#ffffff', width: 200, border: '2px dashed #666' },
      },
    {
      id: 'backend',
      data: { label: 'Backend\n(FastAPI + RAG)' },
      position: { x: 250, y: 250 },
      style: { background: '#d4edda', width: 200 },
    },
    {
      id: 'chromadb',
      data: { label: 'ChromaDB\n(Vector Database)' },
      position: { x: 100, y: 400 },
      style: { background: '#fff3cd' },
    },
    {
      id: 'openai',
      data: { label: 'OpenAI API\n(Embedding + GPT-4)' },
      position: { x: 450, y: 400 },
      style: { background: '#f8d7da' },
    },
  ];

  const edges: Edge[] = [
    { id: 'u-f', source: 'user', target: 'frontend', label: 'Query', animated: true, style: { stroke: '#007bff' }, markerEnd: { type: MarkerType.ArrowClosed } },
    { id: 'f-u', source: 'frontend', target: 'user', label: '', animated: true, style: { stroke: '#28a745' }, markerEnd: { type: MarkerType.ArrowClosed } },
    { id: 'f-b', source: 'frontend', target: 'backend', label: '', animated: true, style: { stroke: '#007bff' }, markerEnd: { type: MarkerType.ArrowClosed } },
    { id: 'f-m', source: 'frontend', target: 'mapbox', label: '', animated: true, style: { stroke: '#800080' }, markerEnd: { type: MarkerType.ArrowClosed } },
    { id: 'm-f', source: 'mapbox', target: 'frontend', label: '', animated: true, style: { stroke: '#800080' }, markerEnd: { type: MarkerType.ArrowClosed } },
    { id: 'g-f', source: 'google maps', target: 'frontend', label: '', animated: true, style: { stroke: '#5e45d9' }, markerEnd: { type: MarkerType.ArrowClosed } },
    { id: 'f-g', source: 'frontend', target: 'google maps', label: '', animated: true, style: { stroke: '#5e45d9' }, markerEnd: { type: MarkerType.ArrowClosed } },
    { id: 'b-f', source: 'backend', target: 'frontend', label: 'Recommendation\n+ Service List', animated: true, style: { stroke: '#28a745' }, markerEnd: { type: MarkerType.ArrowClosed } },
    { id: 'b-c', source: 'backend', target: 'chromadb', label: 'RAG Retrieval', animated: true, style: { stroke: '#ffc107' }, markerEnd: { type: MarkerType.ArrowClosed } },
    { id: 'c-b', source: 'chromadb', target: 'backend', label: '', animated: true, style: { stroke: '#ffc107' }, markerEnd: { type: MarkerType.ArrowClosed } },
    { id: 'b-o', source: 'backend', target: 'openai', label: '', animated: true, style: { stroke: '#dc3545' }, markerEnd: { type: MarkerType.ArrowClosed } },
    { id: 'o-b', source: 'openai', target: 'backend', label: 'Embedding + LLM', animated: true, style: { stroke: '#dc3545' }, markerEnd: { type: MarkerType.ArrowClosed } },
  ];

  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
      >
        <Background />
        <Controls />
        <MiniMap />
        <Panel position="top-right">
          <div style={{ background: 'white', padding: '20px', borderRadius: '5px' }}>
            <h3 style={{ marginBottom: '15px' }}>Legend:</h3>
            <ul style={{ listStyleType: 'none', padding: 0 }}>
              <li style={{color: '#007bff'}}>● User query flow</li>
              <li style={{color: '#ffc107'}}>● RAG retrieval</li>
              <li style={{color: '#dc3545'}}>● OpenAI API interaction</li>
              <li style={{color: '#28a745'}}>● Results and recommendations</li>
              <li style={{color: '#800080'}}>● Mapbox API interaction</li>
              <li style={{color: '#5e45d9'}}>● Google Maps API interaction</li>
            </ul>
            <h3 style={{ marginBottom: '15px' }}></h3>
            <p>The Frontend integrates Mapbox for displaying service locations.</p>
          </div>
        </Panel>
      </ReactFlow>
    </div>
  );
};

export default ArchitectureDiagram;
