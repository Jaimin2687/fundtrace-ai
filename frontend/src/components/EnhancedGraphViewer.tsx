"use client";

import { useEffect, useMemo, useRef, useState, useCallback } from "react";
import dynamic from "next/dynamic";
import { motion, AnimatePresence } from "framer-motion";
import { GraphEdge, GraphNode } from "@/lib/api";
import * as THREE from "three";
import { ZoomIn, ZoomOut, Maximize2, X, AlertTriangle, Shield, Eye } from "lucide-react";

const ForceGraph3D = dynamic(() => import("react-force-graph-3d"), { ssr: false });

type GraphCanvasNode = GraphNode & {
  id: string;
  x?: number;
  y?: number;
  z?: number;
};

type GraphCanvasLink = {
  source: string;
  target: string;
  is_suspicious?: boolean;
  pattern?: string | null;
};

// Pattern-based color scheme
const PATTERN_COLORS: Record<string, number> = {
  "Round-tripping": 0xf43f5e,  // Crimson red
  "Round-Tripping": 0xf43f5e,
  "Layering": 0xf59e0b,        // Amber/yellow
  "Layering - Cash Out": 0xf59e0b,
  "Structuring": 0x8b5cf6,     // Purple
  "Smurfing": 0xec4899,        // Pink
  "Dormant Account Activated": 0x06b6d4, // Cyan
  "Suspicious Transfer": 0xef4444,
};

const PATTERN_COLOR_CSS: Record<string, string> = {
  "Round-tripping": "text-rose-400",
  "Round-Tripping": "text-rose-400",
  "Layering": "text-amber-400",
  "Layering - Cash Out": "text-amber-400",
  "Structuring": "text-purple-400",
  "Smurfing": "text-pink-400",
  "Dormant Account Activated": "text-cyan-400",
  "Suspicious Transfer": "text-red-400",
};

const PATTERN_BG_CSS: Record<string, string> = {
  "Round-tripping": "border-rose-500/40 bg-rose-500/10",
  "Round-Tripping": "border-rose-500/40 bg-rose-500/10",
  "Layering": "border-amber-500/40 bg-amber-500/10",
  "Layering - Cash Out": "border-amber-500/40 bg-amber-500/10",
  "Structuring": "border-purple-500/40 bg-purple-500/10",
  "Smurfing": "border-pink-500/40 bg-pink-500/10",
  "Dormant Account Activated": "border-cyan-500/40 bg-cyan-500/10",
  "Suspicious Transfer": "border-red-500/40 bg-red-500/10",
};

function getPatternFromScore(score: number): string {
  if (score >= 0.95) return "Round-tripping";
  if (score >= 0.85) return "Layering";
  if (score >= 0.75) return "Structuring";
  return "Normal";
}

interface EnhancedGraphViewerProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  highlightTxId?: string;
  onNodeClick?: (txId: string) => void;
}

export default function EnhancedGraphViewer({
  nodes,
  edges,
  highlightTxId,
  onNodeClick,
}: EnhancedGraphViewerProps) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const graphRef = useRef<any>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 900, height: 600 });
  const [selectedNode, setSelectedNode] = useState<GraphCanvasNode | null>(null);
  const hasZoomedRef = useRef(false);

  useEffect(() => {
    const update = () => {
      if (containerRef.current) {
        setDimensions({
          width: containerRef.current.offsetWidth,
          height: containerRef.current.offsetHeight,
        });
      }
    };
    update();
    window.addEventListener("resize", update);
    return () => window.removeEventListener("resize", update);
  }, []);

  // Reset zoom flag when data changes
  useEffect(() => {
    hasZoomedRef.current = false;
  }, [nodes]);

  const graphData = useMemo<{ nodes: GraphCanvasNode[]; links: GraphCanvasLink[] }>(
    () => ({
      nodes: nodes.map((node) => ({ id: node.txId, ...node })),
      links: edges.map((edge) => ({
        source: edge.source,
        target: edge.target,
        is_suspicious: edge.is_suspicious ?? false,
        pattern: edge.pattern ?? null,
      })),
    }),
    [nodes, edges]
  );

  // Zoom controls
  const handleZoomIn = useCallback(() => {
    if (!graphRef.current) return;
    const cam = graphRef.current.camera();
    const pos = cam.position;
    graphRef.current.cameraPosition(
      { x: pos.x * 0.7, y: pos.y * 0.7, z: pos.z * 0.7 },
      undefined,
      400
    );
  }, []);

  const handleZoomOut = useCallback(() => {
    if (!graphRef.current) return;
    const cam = graphRef.current.camera();
    const pos = cam.position;
    graphRef.current.cameraPosition(
      { x: pos.x * 1.4, y: pos.y * 1.4, z: pos.z * 1.4 },
      undefined,
      400
    );
  }, []);

  const handleFitView = useCallback(() => {
    if (!graphRef.current || graphData.nodes.length === 0) return;
    graphRef.current.zoomToFit(600, 40);
  }, [graphData.nodes.length]);

  // Custom 3D node rendering with pattern-based colors and glow
  const nodeThreeObject = useCallback(
    (node: any) => {
      const n = node as GraphCanvasNode;
      const isHighlighted = node.id === highlightTxId;
      const isSelected = node.id === selectedNode?.id;
      const isFraud = node.aml_label === "fraud";
      const isLegit = node.aml_label === "legit";

      // Determine pattern from risk score
      const pattern = isFraud ? getPatternFromScore(node.risk_score || 0) : "Normal";

      // Size: bigger for high-risk, selected, or highlighted
      const baseSize = 6 + (node.risk_score || 0) * 10;
      const size = isHighlighted || isSelected ? baseSize * 1.6 : baseSize;

      // Color based on pattern for fraud, otherwise status-based
      let color: number;
      if (isHighlighted || isSelected) {
        color = 0x22d3ee; // Neon Cyan
      } else if (isFraud) {
        color = PATTERN_COLORS[pattern] || 0xf43f5e;
      } else if (isLegit) {
        color = 0x34d399;
      } else {
        color = 0x64748b;
      }

      const group = new THREE.Group();

      // Core sphere
      const geometry = new THREE.SphereGeometry(size, 20, 20);
      const material = new THREE.MeshPhongMaterial({
        color,
        emissive: color,
        emissiveIntensity: isFraud || isHighlighted || isSelected ? 0.7 : 0.15,
        shininess: 100,
        transparent: true,
        opacity: 0.95,
      });
      const mesh = new THREE.Mesh(geometry, material);
      group.add(mesh);

      // Outer glow for fraud/highlighted/selected nodes
      if (isFraud || isHighlighted || isSelected) {
        const glowGeometry = new THREE.SphereGeometry(size * 1.5, 16, 16);
        const glowMaterial = new THREE.MeshBasicMaterial({
          color,
          transparent: true,
          opacity: 0.12,
        });
        const glowMesh = new THREE.Mesh(glowGeometry, glowMaterial);
        group.add(glowMesh);
      }

      // Label sprite for fraud nodes
      if (isFraud && size > 6) {
        const canvas = document.createElement("canvas");
        const ctx = canvas.getContext("2d")!;
        canvas.width = 256;
        canvas.height = 64;
        ctx.font = "bold 24px monospace";
        ctx.fillStyle = "#ffffff";
        ctx.textAlign = "center";
        ctx.fillText(node.txId.slice(0, 12), 128, 40);
        const texture = new THREE.CanvasTexture(canvas);
        const spriteMaterial = new THREE.SpriteMaterial({
          map: texture,
          transparent: true,
          opacity: 0.8,
        });
        const sprite = new THREE.Sprite(spriteMaterial);
        sprite.scale.set(size * 4, size, 1);
        sprite.position.set(0, size + 6, 0);
        group.add(sprite);
      }

      return group;
    },
    [highlightTxId, selectedNode?.id]
  );

  const handleNodeClickInternal = useCallback(
    (node: GraphCanvasNode) => {
      setSelectedNode(node);
      if (onNodeClick) onNodeClick(node.id);
      // Fly camera to node
      if (graphRef.current) {
        const x = typeof node.x === "number" ? node.x : 0;
        const y = typeof node.y === "number" ? node.y : 0;
        const z = typeof node.z === "number" ? node.z : 0;
        graphRef.current.cameraPosition(
          { x: x + 40, y: y + 30, z: z + 80 },
          node,
          800
        );
      }
    },
    [onNodeClick]
  );

  return (
    <div ref={containerRef} className="relative h-full w-full">
      {nodes.length === 0 ? (
        <div className="flex h-full items-center justify-center">
          <div className="text-center">
            <div className="mx-auto mb-4 h-16 w-16 rounded-full border border-white/10 bg-white/5 flex items-center justify-center">
              <Eye className="h-7 w-7 text-slate-500" />
            </div>
            <div className="text-sm text-slate-400">Awaiting graph payload...</div>
            <div className="mt-1 text-xs text-slate-600">
              Click &quot;Load Clusters&quot; or select an alert
            </div>
          </div>
        </div>
      ) : (
        <>
          <ForceGraph3D
            ref={graphRef}
            width={dimensions.width}
            height={dimensions.height}
            graphData={graphData}
            backgroundColor="#070b12"
            showNavInfo={false}
            nodeThreeObject={nodeThreeObject}
            nodeThreeObjectExtend={false}
              linkColor={(link: any) =>
                link.is_suspicious ? "rgba(244,63,94,0.7)" : "rgba(148,163,184,0.35)"
              }
              linkWidth={(link: any) => (link.is_suspicious ? 2 : 0.8)}
            linkDirectionalParticles={(link: any) =>
              link.is_suspicious ? 5 : 0
            }
            linkDirectionalParticleWidth={(link: any) =>
              link.is_suspicious ? 2 : 0.8
            }
            linkDirectionalParticleSpeed={(link: any) =>
              link.is_suspicious ? 0.008 : 0.003
            }
            linkDirectionalArrowLength={3}
            linkDirectionalArrowRelPos={1}
            onNodeClick={(node: any) => handleNodeClickInternal(node as GraphCanvasNode)}
            onBackgroundClick={() => setSelectedNode(null)}
            onEngineStop={() => {
              if (!hasZoomedRef.current && graphRef.current && graphData.nodes.length > 0) {
                hasZoomedRef.current = true;
                // Auto-zoom to fit all nodes with nice padding
                graphRef.current.zoomToFit(800, 60);
              }
            }}
          />

          {/* Zoom Controls */}
          <div className="absolute right-4 top-4 flex flex-col gap-2 z-20">
            <button
              onClick={handleZoomIn}
              className="glass-panel rounded-xl p-2.5 text-slate-300 transition hover:text-white hover:border-cyan-400/40"
              title="Zoom in"
            >
              <ZoomIn className="h-4 w-4" />
            </button>
            <button
              onClick={handleZoomOut}
              className="glass-panel rounded-xl p-2.5 text-slate-300 transition hover:text-white hover:border-cyan-400/40"
              title="Zoom out"
            >
              <ZoomOut className="h-4 w-4" />
            </button>
            <button
              onClick={handleFitView}
              className="glass-panel rounded-xl p-2.5 text-slate-300 transition hover:text-white hover:border-cyan-400/40"
              title="Fit to view"
            >
              <Maximize2 className="h-4 w-4" />
            </button>
          </div>

          {/* Node count badge */}
          <div className="absolute top-4 left-4 z-20">
            <div className="glass-panel rounded-xl px-3 py-2 text-xs text-slate-400">
              {graphData.nodes.length} nodes · {graphData.links.length} edges
            </div>
          </div>

          {/* Color Legend */}
          <div className="absolute bottom-4 left-4 z-20">
            <div className="glass-panel rounded-xl p-3 space-y-2 text-xs">
              <div className="uppercase tracking-[0.2em] text-slate-500 mb-2">Pattern Legend</div>
              {[
                { color: "bg-rose-500", label: "Round-tripping" },
                { color: "bg-amber-500", label: "Layering" },
                { color: "bg-purple-500", label: "Structuring" },
                { color: "bg-emerald-400", label: "Legit" },
                { color: "bg-cyan-400", label: "Selected" },
              ].map((item) => (
                <div key={item.label} className="flex items-center gap-2">
                  <div className={`h-2.5 w-2.5 rounded-full ${item.color}`} />
                  <span className="text-slate-300">{item.label}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Node Detail Panel */}
          <AnimatePresence>
            {selectedNode && (
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ type: "spring", stiffness: 300, damping: 30 }}
                className="absolute bottom-4 right-4 z-20 w-80"
              >
                <div className="glass-panel rounded-2xl border border-white/10 p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      {selectedNode.aml_label === "fraud" ? (
                        <AlertTriangle className="h-4 w-4 text-rose-400" />
                      ) : (
                        <Shield className="h-4 w-4 text-emerald-400" />
                      )}
                      <span className="text-xs uppercase tracking-[0.2em] text-slate-400">
                        Node Details
                      </span>
                    </div>
                    <button
                      onClick={() => setSelectedNode(null)}
                      className="rounded-lg p-1 text-slate-400 transition hover:text-white hover:bg-white/10"
                    >
                      <X className="h-3.5 w-3.5" />
                    </button>
                  </div>

                  {/* Transaction ID */}
                  <div className="mb-3">
                    <div className="text-[10px] uppercase tracking-[0.2em] text-slate-500">
                      Transaction ID
                    </div>
                    <div className="mt-0.5 font-mono text-xs text-slate-200 break-all">
                      {selectedNode.txId}
                    </div>
                  </div>

                  {/* Status + Pattern */}
                  <div className="flex items-center gap-2 mb-3">
                    <span
                      className={`rounded-full border px-2 py-0.5 text-[10px] uppercase tracking-wider ${
                        selectedNode.aml_label === "fraud"
                          ? "border-rose-500/40 bg-rose-500/10 text-rose-300"
                          : selectedNode.aml_label === "legit"
                          ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-300"
                          : "border-slate-500/40 bg-slate-500/10 text-slate-300"
                      }`}
                    >
                      {selectedNode.aml_label || "unknown"}
                    </span>
                    {selectedNode.aml_label === "fraud" && (
                      <span
                        className={`rounded-full border px-2 py-0.5 text-[10px] uppercase tracking-wider ${
                          PATTERN_BG_CSS[getPatternFromScore(selectedNode.risk_score || 0)] ||
                          "border-slate-500/40 bg-slate-500/10"
                        } ${
                          PATTERN_COLOR_CSS[getPatternFromScore(selectedNode.risk_score || 0)] ||
                          "text-slate-300"
                        }`}
                      >
                        {getPatternFromScore(selectedNode.risk_score || 0)}
                      </span>
                    )}
                  </div>

                  {/* Risk Score Bar */}
                  <div className="mb-3">
                    <div className="flex items-center justify-between text-[10px] text-slate-500 mb-1">
                      <span>Risk Score</span>
                      <span className="text-slate-300 font-mono">
                        {((selectedNode.risk_score || 0) * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="h-2 w-full rounded-full bg-slate-800 overflow-hidden">
                      <div
                        className={`h-2 rounded-full transition-all duration-500 ${
                          (selectedNode.risk_score || 0) >= 0.85
                            ? "bg-rose-500"
                            : (selectedNode.risk_score || 0) >= 0.7
                            ? "bg-amber-500"
                            : "bg-emerald-500"
                        }`}
                        style={{ width: `${(selectedNode.risk_score || 0) * 100}%` }}
                      />
                    </div>
                  </div>

                  {/* Time Step */}
                  {selectedNode.time_step !== undefined && (
                    <div className="mb-3">
                      <div className="text-[10px] uppercase tracking-[0.2em] text-slate-500">
                        Time Step
                      </div>
                      <div className="mt-0.5 font-mono text-xs text-slate-200">
                        T+{selectedNode.time_step}
                      </div>
                    </div>
                  )}

                  {/* Action buttons */}
                  <div className="flex gap-2 mt-3 pt-3 border-t border-white/10">
                    <button
                      onClick={() => onNodeClick?.(selectedNode.id)}
                      className="flex-1 rounded-xl border border-cyan-400/30 bg-cyan-400/10 px-3 py-2 text-[10px] uppercase tracking-[0.15em] text-cyan-200 transition hover:bg-cyan-400/20"
                    >
                      View Evidence
                    </button>
                    <button
                      onClick={() => {
                        navigator.clipboard.writeText(selectedNode.txId);
                      }}
                      className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-[10px] uppercase tracking-[0.15em] text-slate-300 transition hover:bg-white/10"
                    >
                      Copy ID
                    </button>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </>
      )}
    </div>
  );
}
