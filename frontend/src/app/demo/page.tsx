'use client';

import { useState } from 'react';
import GraphViewer from '@/components/GraphViewer';
import {
  fetchGraphFocus,
  fetchEvidence,
  GraphNode,
  GraphEdge,
  EvidencePackage,
} from '@/lib/api';
import { Play, CheckCircle, Loader2 } from 'lucide-react';

// Hardcoded fraud transaction ID from Elliptic dataset (class=1)
const DEMO_TX_ID = '1';

interface DemoStep {
  id: number;
  title: string;
  description: string;
  action: () => Promise<void>;
  completed: boolean;
}

export default function DemoPage() {
  const [currentStep, setCurrentStep] = useState<number | null>(null);
  const [graphNodes, setGraphNodes] = useState<GraphNode[]>([]);
  const [graphEdges, setGraphEdges] = useState<GraphEdge[]>([]);
  const [evidence, setEvidence] = useState<EvidencePackage | null>(null);
  const [loading, setLoading] = useState(false);
  const [completedSteps, setCompletedSteps] = useState<Set<number>>(new Set());

  const steps: DemoStep[] = [
    {
      id: 1,
      title: '1. Detect Alert',
      description: 'System identifies suspicious transaction in real-time',
      action: async () => {
        // Simulate alert detection
        await new Promise((resolve) => setTimeout(resolve, 1000));
        setCurrentStep(1);
      },
      completed: completedSteps.has(1),
    },
    {
      id: 2,
      title: '2. Trace the Chain',
      description: 'Analyze transaction network and connected accounts',
      action: async () => {
        const data = await fetchGraphFocus(DEMO_TX_ID, 3);
        setGraphNodes(data.nodes);
        setGraphEdges(data.edges);
        setCurrentStep(2);
      },
      completed: completedSteps.has(2),
    },
    {
      id: 3,
      title: '3. View Pattern',
      description: 'Identify fraud patterns and risk indicators',
      action: async () => {
        // Pattern is already visible in the graph
        await new Promise((resolve) => setTimeout(resolve, 1000));
        setCurrentStep(3);
      },
      completed: completedSteps.has(3),
    },
    {
      id: 4,
      title: '4. Generate Evidence',
      description: 'Create comprehensive evidence package for investigation',
      action: async () => {
        const data = await fetchEvidence(DEMO_TX_ID);
        setEvidence(data);
        setCurrentStep(4);
      },
      completed: completedSteps.has(4),
    },
  ];

  const runStep = async (stepId: number) => {
    setLoading(true);
    try {
      await steps[stepId - 1].action();
      setCompletedSteps((prev) => new Set([...prev, stepId]));
    } catch (error) {
      console.error(`Failed to run step ${stepId}:`, error);
    } finally {
      setLoading(false);
    }
  };

  const runFullDemo = async () => {
    setCompletedSteps(new Set());
    setCurrentStep(null);
    setGraphNodes([]);
    setGraphEdges([]);
    setEvidence(null);

    for (let i = 0; i < steps.length; i++) {
      await new Promise((resolve) => setTimeout(resolve, 2000));
      await runStep(i + 1);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-slate-100 mb-2">
            FundTrace AI - Demo Walkthrough
          </h1>
          <p className="text-slate-400">
            Scripted demonstration of fraud detection capabilities for judges
          </p>
        </div>

        {/* Run Full Demo Button */}
        <div className="mb-8">
          <button
            onClick={runFullDemo}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:cursor-not-allowed text-white px-6 py-3 rounded-lg flex items-center gap-2 transition-colors text-lg font-semibold"
          >
            {loading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Play className="w-5 h-5" />
            )}
            Run Full Demo
          </button>
        </div>

        {/* Steps Grid */}
        <div className="grid grid-cols-4 gap-4 mb-8">
          {steps.map((step) => (
            <button
              key={step.id}
              onClick={() => runStep(step.id)}
              disabled={loading}
              className={`p-6 rounded-lg border-2 transition-all text-left ${
                currentStep === step.id
                  ? 'bg-blue-600/20 border-blue-500'
                  : step.completed
                  ? 'bg-green-600/10 border-green-500/30'
                  : 'bg-slate-900 border-slate-800 hover:border-slate-700'
              } ${loading ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'}`}
            >
              <div className="flex items-start justify-between mb-3">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${
                    currentStep === step.id
                      ? 'bg-blue-500 text-white'
                      : step.completed
                      ? 'bg-green-500 text-white'
                      : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  {step.completed ? <CheckCircle className="w-5 h-5" /> : step.id}
                </div>
                {loading && currentStep === step.id && (
                  <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />
                )}
              </div>
              <h3 className="text-lg font-semibold text-slate-100 mb-2">{step.title}</h3>
              <p className="text-sm text-slate-400">{step.description}</p>
            </button>
          ))}
        </div>

        {/* Content Area */}
        <div className="grid grid-cols-2 gap-8">
          {/* Graph Visualization */}
          <div className="bg-slate-900 rounded-lg border border-slate-800 overflow-hidden">
            <div className="p-4 border-b border-slate-800">
              <h2 className="text-lg font-semibold text-slate-100">Transaction Network</h2>
            </div>
            <div className="h-[500px]">
              <GraphViewer
                nodes={graphNodes}
                edges={graphEdges}
                highlightTxId={currentStep === 2 || currentStep === 3 ? DEMO_TX_ID : undefined}
              />
            </div>
          </div>

          {/* Evidence Package */}
          <div className="bg-slate-900 rounded-lg border border-slate-800 overflow-hidden">
            <div className="p-4 border-b border-slate-800">
              <h2 className="text-lg font-semibold text-slate-100">Evidence Package</h2>
            </div>
            <div className="h-[500px] overflow-y-auto p-4">
              {!evidence ? (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center">
                    <div className="text-slate-500 mb-2">No evidence generated yet</div>
                    <div className="text-slate-600 text-sm">
                      Run step 4 to generate evidence package
                    </div>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  {/* Transaction ID */}
                  <div>
                    <label className="text-xs text-slate-500 mb-1 block">Transaction ID</label>
                    <div className="bg-slate-800/50 rounded p-2 font-mono text-sm text-slate-200 break-all">
                      {evidence.txId}
                    </div>
                  </div>

                  {/* Narrative */}
                  <div>
                    <label className="text-xs text-slate-500 mb-1 block">Narrative</label>
                    <div className="bg-slate-800/50 rounded p-3 text-sm text-slate-300 leading-relaxed">
                      {evidence.narrative}
                    </div>
                  </div>

                  {/* Total Amount */}
                  <div>
                    <label className="text-xs text-slate-500 mb-1 block">Total Amount</label>
                    <div className="bg-slate-800/50 rounded p-2 text-lg font-semibold text-slate-200">
                      {new Intl.NumberFormat('en-IN', {
                        style: 'currency',
                        currency: 'INR',
                        maximumFractionDigits: 0,
                      }).format(evidence.total_amount)}
                    </div>
                  </div>

                  {/* Chain Summary */}
                  <div>
                    <label className="text-xs text-slate-500 mb-2 block">Chain Summary</label>
                    <div className="space-y-2">
                      {evidence.chain.slice(0, 5).map((txId, index) => (
                        <div
                          key={index}
                          className="bg-slate-800/50 rounded p-2 flex items-center justify-between"
                        >
                          <div className="flex items-center gap-2">
                            <div className="w-6 h-6 rounded-full bg-blue-500/20 text-blue-400 text-xs flex items-center justify-center font-semibold">
                              {index + 1}
                            </div>
                            <span className="text-xs font-mono text-slate-400">
                              {txId.slice(0, 12)}...
                            </span>
                          </div>
                          <span className="text-xs text-slate-500">
                            {evidence.patterns[index]}
                          </span>
                        </div>
                      ))}
                      {evidence.chain.length > 5 && (
                        <div className="text-xs text-slate-500 text-center">
                          +{evidence.chain.length - 5} more transactions
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Generated At */}
                  <div>
                    <label className="text-xs text-slate-500 mb-1 block">Generated At</label>
                    <div className="bg-slate-800/50 rounded p-2 text-xs text-slate-400">
                      {new Date(evidence.generated_at).toLocaleString()}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Demo Info */}
        <div className="mt-8 bg-blue-900/20 border border-blue-800/30 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-400 mb-2">Demo Information</h3>
          <div className="text-sm text-slate-300 space-y-2">
            <p>
              <strong>Dataset:</strong> Elliptic Bitcoin Transaction Dataset
            </p>
            <p>
              <strong>Demo Transaction:</strong> {DEMO_TX_ID} (Confirmed Fraud)
            </p>
            <p>
              <strong>Features:</strong> Real-time detection, network analysis, pattern
              recognition, evidence generation
            </p>
            <p>
              <strong>Technology:</strong> Neo4j Graph Database, XGBoost ML, FastAPI, Next.js
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
