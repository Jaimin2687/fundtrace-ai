'use client';

import { useEffect, useRef, useState } from 'react';
import dynamic from 'next/dynamic';
import { GraphNode, GraphEdge } from '@/lib/api';

// Dynamically import ForceGraph2D with SSR disabled
const ForceGraph2D = dynamic(() => import('react-force-graph-2d'), {
  ssr: false,
});

interface GraphViewerProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  highlightTxId?: string;
  onNodeClick?: (txId: string) => void;
}

export default function GraphViewer({
  nodes,
  edges,
  highlightTxId,
  onNodeClick,
}: GraphViewerProps) {
  const graphRef = useRef<any>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const containerRef = useRef<HTMLDivElement>(null);

  // Update dimensions on mount and resize
  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        setDimensions({
          width: containerRef.current.offsetWidth,
          height: containerRef.current.offsetHeight,
        });
      }
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  // Transform data for react-force-graph
  const graphData = {
    nodes: nodes.map((node) => ({
      id: node.txId,
      ...node,
    })),
    links: edges.map((edge) => ({
      source: edge.source,
      target: edge.target,
    })),
  };

  // Node color based on aml_label
  const getNodeColor = (node: any) => {
    if (node.id === highlightTxId) {
      return '#3b82f6'; // Blue for highlighted
    }
    
    switch (node.aml_label) {
      case 'fraud':
        return '#ef4444'; // Red
      case 'legit':
        return '#22c55e'; // Green
      default:
        return '#6b7280'; // Gray
    }
  };

  // Node size based on risk_score
  const getNodeSize = (node: any) => {
    const baseSize = node.id === highlightTxId ? 8 : 4;
    const riskMultiplier = node.risk_score || 0;
    return baseSize + (riskMultiplier * 8); // Min 4, max 12 (or 16 if highlighted)
  };

  // Node canvas rendering with pulsing effect for highlighted node
  const paintNode = (node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
    const size = getNodeSize(node);
    const color = getNodeColor(node);

    // Draw pulsing ring for highlighted node
    if (node.id === highlightTxId) {
      const time = Date.now() / 1000;
      const pulseSize = size + Math.sin(time * 3) * 2;
      
      ctx.beginPath();
      ctx.arc(node.x, node.y, pulseSize, 0, 2 * Math.PI);
      ctx.strokeStyle = color;
      ctx.lineWidth = 2 / globalScale;
      ctx.stroke();
    }

    // Draw node
    ctx.beginPath();
    ctx.arc(node.x, node.y, size, 0, 2 * Math.PI);
    ctx.fillStyle = color;
    ctx.fill();

    // Draw border
    ctx.strokeStyle = '#1e293b';
    ctx.lineWidth = 1 / globalScale;
    ctx.stroke();

    // Draw label for highlighted node
    if (node.id === highlightTxId) {
      const label = node.id.slice(0, 8);
      const fontSize = 12 / globalScale;
      ctx.font = `${fontSize}px Sans-Serif`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = '#e2e8f0';
      ctx.fillText(label, node.x, node.y - size - 8);
    }
  };

  return (
    <div ref={containerRef} className="w-full h-full bg-slate-950">
      {nodes.length === 0 ? (
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="text-slate-500 text-lg mb-2">No graph data</div>
            <div className="text-slate-600 text-sm">
              Select an alert or load fraud clusters to visualize
            </div>
          </div>
        </div>
      ) : (
        <ForceGraph2D
          ref={graphRef}
          graphData={graphData}
          width={dimensions.width}
          height={dimensions.height}
          backgroundColor="#0f172a"
          nodeCanvasObject={paintNode}
          nodePointerAreaPaint={(node: any, color: string, ctx: CanvasRenderingContext2D) => {
            ctx.fillStyle = color;
            const size = getNodeSize(node);
            ctx.beginPath();
            ctx.arc(node.x, node.y, size, 0, 2 * Math.PI);
            ctx.fill();
          }}
          onNodeClick={(node: any) => {
            if (onNodeClick) {
              onNodeClick(node.id);
            }
          }}
          linkColor={() => '#334155'}
          linkWidth={1}
          linkDirectionalArrowLength={3}
          linkDirectionalArrowRelPos={1}
          linkDirectionalArrowColor={() => '#475569'}
          cooldownTicks={100}
          onEngineStop={() => {
            if (graphRef.current && highlightTxId) {
              // Center on highlighted node
              const node = graphData.nodes.find((n) => n.id === highlightTxId);
              if (node) {
                graphRef.current.centerAt(node.x, node.y, 1000);
                graphRef.current.zoom(2, 1000);
              }
            }
          }}
        />
      )}
    </div>
  );
}
