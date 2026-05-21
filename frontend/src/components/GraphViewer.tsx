'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import dynamic from 'next/dynamic';
import type { ForceGraphMethods } from 'react-force-graph-2d';
import { GraphNode, GraphEdge } from '@/lib/api';

// Dynamically import ForceGraph2D with SSR disabled
const ForceGraph2D = dynamic(() => import('react-force-graph-2d'), {
  ssr: false,
});

type GraphCanvasNode = GraphNode & {
  id: string;
  x?: number;
  y?: number;
};

type GraphCanvasLink = {
  source: string;
  target: string;
};

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
  const graphData = useMemo<{ nodes: GraphCanvasNode[]; links: GraphCanvasLink[] }>(
    () => ({
      nodes: nodes.map((node) => ({
        id: node.txId,
        ...node,
      })),
      links: edges.map((edge) => ({
        source: edge.source,
        target: edge.target,
      })),
    }),
    [nodes, edges]
  );

  // Node color based on aml_label
  const getNodeColor = (node: GraphCanvasNode) => {
    if (node.id === highlightTxId) {
      return '#22d3ee';
    }
    
    switch (node.aml_label) {
      case 'fraud':
        return '#f43f5e';
      case 'legit':
        return '#34d399';
      default:
        return '#94a3b8';
    }
  };

  // Node size based on risk_score
  const getNodeSize = (node: GraphCanvasNode) => {
    const baseSize = node.id === highlightTxId ? 8 : 4;
    const riskMultiplier = node.risk_score || 0;
    return baseSize + (riskMultiplier * 8); // Min 4, max 12 (or 16 if highlighted)
  };

  // Node canvas rendering with pulsing effect for highlighted node
  const paintNode = (
    node: GraphCanvasNode,
    ctx: CanvasRenderingContext2D,
    globalScale: number
  ) => {
    const size = getNodeSize(node);
    const color = getNodeColor(node);
    const x = node.x ?? 0;
    const y = node.y ?? 0;

    // Draw pulsing ring for highlighted node
    if (node.id === highlightTxId) {
      const time = Date.now() / 1000;
      const pulseSize = size + Math.sin(time * 3) * 2;
      
      ctx.beginPath();
      ctx.arc(x, y, pulseSize, 0, 2 * Math.PI);
      ctx.strokeStyle = color;
      ctx.lineWidth = 2 / globalScale;
      ctx.stroke();
    }

    // Draw node
    ctx.beginPath();
    ctx.arc(x, y, size, 0, 2 * Math.PI);
    ctx.fillStyle = color;
    ctx.fill();

    // Draw border
    ctx.strokeStyle = '#0f172a';
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
      ctx.fillText(label, x, y - size - 8);
    }
  };

  return (
    <div ref={containerRef} className="w-full h-full bg-[#070b12]">
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
        // @ts-ignore
        <ForceGraph2D
          ref={graphRef}
          graphData={graphData}
          width={dimensions.width}
          height={dimensions.height}
          backgroundColor="#070b12"
          nodeCanvasObject={paintNode}
          nodePointerAreaPaint={(
            node: GraphCanvasNode,
            color: string,
            ctx: CanvasRenderingContext2D
          ) => {
            ctx.fillStyle = color;
            const size = getNodeSize(node);
            const x = node.x ?? 0;
            const y = node.y ?? 0;
            ctx.beginPath();
            ctx.arc(x, y, size, 0, 2 * Math.PI);
            ctx.fill();
          }}
          onNodeClick={(node: GraphCanvasNode) => {
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
                const x = node.x ?? 0;
                const y = node.y ?? 0;
                graphRef.current.centerAt(x, y, 1000);
                graphRef.current.zoom(2, 1000);
              }
            }
          }}
        />
      )}
    </div>
  );
}
