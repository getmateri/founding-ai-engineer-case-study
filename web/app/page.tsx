'use client';

import { useState, useEffect } from 'react';
import {
  DataSource,
  TermSheet,
  getDataSources,
  startGeneration,
  runGeneration,
  updateField,
  finalizeDocument,
  formatFileSize,
} from '@/lib/api';
import ReactMarkdown from 'react-markdown';

type AppState = 'start' | 'loading' | 'review' | 'complete';

interface FieldMetadata {
  section: string;
  field: string;
  value: string | null;
  confidence: number;
  source: { file: string; location: string } | null;
  reasoning?: string;
  found: boolean;
  derived_from_policy: boolean;
  user_edited: boolean;
  conflicts: Array<{ source: string; value: string; confidence: number }>;
}

export default function Home() {
  const [appState, setAppState] = useState<AppState>('start');
  const [dataSources, setDataSources] = useState<DataSource[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [termSheet, setTermSheet] = useState<TermSheet | null>(null);
  const [previewMarkdown, setPreviewMarkdown] = useState<string>('');
  const [loadingMessage, setLoadingMessage] = useState<string>('Initializing...');
  const [error, setError] = useState<string | null>(null);
  const [editingField, setEditingField] = useState<{ section: string; field: string } | null>(null);
  const [editValue, setEditValue] = useState<string>('');
  const [finalOutputs, setFinalOutputs] = useState<{ [key: string]: string } | null>(null);

  // Load data sources on mount
  useEffect(() => {
    getDataSources()
      .then((res) => setDataSources(res.sources))
      .catch((err) => setError(err.message));
  }, []);

  // Get file icon based on type
  const getFileIcon = (type: string) => {
    switch (type) {
      case 'excel': return '📊';
      case 'markdown': return '📝';
      case 'zip': return '📦';
      case 'pdf': return '📄';
      case 'docx': return '📃';
      default: return '📁';
    }
  };

  // Start document generation
  const handleStartGeneration = async () => {
    setAppState('loading');
    setError(null);
    setLoadingMessage('Starting generation...');

    try {
      // Start session
      const startRes = await startGeneration('term_sheet');
      setSessionId(startRes.session_id);
      setLoadingMessage('Loading source files...');

      // Run extraction (this is the long call)
      setLoadingMessage('Extracting data from sources... This may take a minute.');
      const result = await runGeneration(startRes.session_id);

      if (result.status === 'error') {
        throw new Error(result.error || 'Generation failed');
      }

      setTermSheet(result.term_sheet || null);
      setPreviewMarkdown(result.preview_markdown || '');
      setAppState('review');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setAppState('start');
    }
  };

  // Update a field
  const handleUpdateField = async () => {
    if (!editingField || !sessionId) return;

    try {
      const res = await updateField(
        sessionId,
        editingField.section,
        editingField.field,
        editValue
      );

      if (res.success && res.term_sheet) {
        setTermSheet(res.term_sheet);
        setPreviewMarkdown(res.preview_markdown || '');
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Update failed');
    }

    setEditingField(null);
    setEditValue('');
  };

  // Finalize document
  const handleFinalize = async () => {
    if (!sessionId) return;

    try {
      const res = await finalizeDocument(sessionId);
      if (res.success) {
        setFinalOutputs(res.outputs || null);
        setAppState('complete');
      } else {
        setError(res.message);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Finalize failed');
    }
  };

  // Get all fields with metadata
  const getAllFields = (): FieldMetadata[] => {
    if (!termSheet) return [];

    const fields: FieldMetadata[] = [];
    for (const [sectionName, sectionData] of Object.entries(termSheet.sections)) {
      for (const [fieldName, fieldData] of Object.entries(sectionData)) {
        fields.push({
          section: sectionName,
          field: fieldName,
          value: fieldData.value,
          confidence: fieldData.confidence,
          source: fieldData.source,
          reasoning: fieldData.reasoning,
          found: fieldData.found,
          derived_from_policy: fieldData.derived_from_policy,
          user_edited: fieldData.user_edited,
          conflicts: fieldData.conflicts,
        });
      }
    }
    return fields;
  };

  // Check if all fields have confidence = 1
  const canFinalize = (): boolean => {
    const fields = getAllFields();
    return fields.every((f) => f.confidence === 1.0);
  };

  // Count fields needing review
  const getReviewStats = () => {
    const fields = getAllFields();
    const needsReview = fields.filter((f) => f.confidence < 1.0).length;
    const total = fields.length;
    return { needsReview, total, ready: total - needsReview };
  };

  // Render start screen
  if (appState === 'start') {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center p-8">
        <div className="max-w-2xl w-full">
          <h1 className="text-4xl font-light mb-2 tracking-tight">Document Generator</h1>
          <p className="text-slate-400 mb-8">AI-powered document generation with human review</p>

          {error && (
            <div className="bg-red-900/50 border border-red-700 text-red-200 px-4 py-3 rounded mb-6">
              {error}
            </div>
          )}

          <div className="bg-slate-900 rounded-lg p-6 mb-6 border border-slate-800">
            <h2 className="text-lg font-medium mb-4 text-slate-200">Available Data Sources</h2>
            {dataSources.length === 0 ? (
              <p className="text-slate-500">Loading...</p>
            ) : (
              <ul className="space-y-3">
                {dataSources.map((source) => (
                  <li
                    key={source.name}
                    className="flex items-center justify-between bg-slate-800/50 px-4 py-3 rounded"
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">{getFileIcon(source.type)}</span>
                      <div>
                        <div className="font-mono text-sm">{source.name}</div>
                        <div className="text-xs text-slate-500">{source.type}</div>
                      </div>
                    </div>
                    <span className="text-xs text-slate-500">{formatFileSize(source.size)}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="bg-slate-900 rounded-lg p-6 border border-slate-800">
            <h2 className="text-lg font-medium mb-4 text-slate-200">Document Type</h2>
            <div className="flex gap-4">
              <button
                onClick={handleStartGeneration}
                className="flex-1 bg-emerald-600 hover:bg-emerald-500 text-white px-6 py-4 rounded-lg font-medium transition-colors"
              >
                📋 Generate Term Sheet
              </button>
            </div>
            <p className="text-xs text-slate-500 mt-4">
              The AI will extract data from your sources and generate a term sheet for review.
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Render loading screen
  if (appState === 'loading') {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center p-8">
        <div className="text-center">
          <div className="animate-spin w-12 h-12 border-4 border-emerald-500 border-t-transparent rounded-full mx-auto mb-6"></div>
          <h2 className="text-xl font-medium mb-2">Generating Document</h2>
          <p className="text-slate-400">{loadingMessage}</p>
        </div>
      </div>
    );
  }

  // Render complete screen
  if (appState === 'complete') {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center p-8">
        <div className="max-w-2xl w-full text-center">
          <div className="text-6xl mb-6">✅</div>
          <h1 className="text-3xl font-light mb-4">Document Finalized</h1>
          <p className="text-slate-400 mb-8">Your term sheet has been generated and saved.</p>

          {finalOutputs && (
            <div className="bg-slate-900 rounded-lg p-6 mb-6 border border-slate-800 text-left">
              <h2 className="text-lg font-medium mb-4">Output Files</h2>
              <ul className="space-y-2 font-mono text-sm">
                {Object.entries(finalOutputs).map(([name, path]) => (
                  <li key={name} className="flex justify-between">
                    <span className="text-slate-400">{name}</span>
                    <span className="text-emerald-400">{path}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <button
            onClick={() => {
              setAppState('start');
              setSessionId(null);
              setTermSheet(null);
              setPreviewMarkdown('');
              setFinalOutputs(null);
            }}
            className="bg-slate-700 hover:bg-slate-600 px-6 py-3 rounded-lg transition-colors"
          >
            Start New Document
          </button>
        </div>
      </div>
    );
  }

  // Render review screen (main UI)
  const stats = getReviewStats();
  const fields = getAllFields();

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      {/* Header */}
      <header className="border-b border-slate-800 px-6 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-medium">Term Sheet Review</h1>
          <p className="text-sm text-slate-400">
            {stats.ready}/{stats.total} fields ready •{' '}
            <span className={stats.needsReview > 0 ? 'text-amber-400' : 'text-emerald-400'}>
              {stats.needsReview} need review
            </span>
          </p>
        </div>
        <button
          onClick={handleFinalize}
          disabled={!canFinalize()}
          className={`px-6 py-2 rounded-lg font-medium transition-colors ${
            canFinalize()
              ? 'bg-emerald-600 hover:bg-emerald-500 text-white'
              : 'bg-slate-800 text-slate-500 cursor-not-allowed'
          }`}
        >
          {canFinalize() ? 'Finalize Document' : `${stats.needsReview} fields need review`}
        </button>
      </header>

      {error && (
        <div className="bg-red-900/50 border-b border-red-700 text-red-200 px-6 py-3">
          {error}
          <button onClick={() => setError(null)} className="ml-4 underline">
            Dismiss
          </button>
        </div>
      )}

      {/* Main content */}
      <div className="flex h-[calc(100vh-73px)]">
        {/* Fields panel */}
        <div className="w-1/2 border-r border-slate-800 overflow-y-auto p-6">
          <h2 className="text-lg font-medium mb-4 text-slate-200">Extracted Fields</h2>

          {/* Group by section */}
          {Object.keys(termSheet?.sections || {}).map((sectionName) => (
            <div key={sectionName} className="mb-6">
              <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wide mb-3">
                {sectionName.replace(/_/g, ' ')}
              </h3>

              <div className="space-y-3">
                {fields
                  .filter((f) => f.section === sectionName)
                  .map((field) => (
                    <div
                      key={`${field.section}.${field.field}`}
                      className={`bg-slate-900 rounded-lg p-4 border ${
                        field.confidence < 1.0 ? 'border-amber-600/50' : 'border-slate-800'
                      }`}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="font-mono text-sm text-slate-300">
                          {field.field.replace(/_/g, ' ')}
                        </div>
                        <div
                          className={`text-xs px-2 py-1 rounded ${
                            field.confidence === 1.0
                              ? 'bg-emerald-900/50 text-emerald-300'
                              : 'bg-amber-900/50 text-amber-300'
                          }`}
                        >
                          {field.confidence === 1.0 ? '✓ Confirmed' : '⚠ Needs Review'}
                        </div>
                      </div>

                      {/* Value */}
                      {editingField?.section === field.section &&
                      editingField?.field === field.field ? (
                        <div className="mb-3">
                          <input
                            type="text"
                            value={editValue}
                            onChange={(e) => setEditValue(e.target.value)}
                            className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm"
                            autoFocus
                          />
                          <div className="flex gap-2 mt-2">
                            <button
                              onClick={handleUpdateField}
                              className="bg-emerald-600 hover:bg-emerald-500 px-3 py-1 rounded text-sm"
                            >
                              Save
                            </button>
                            <button
                              onClick={() => setEditingField(null)}
                              className="bg-slate-700 hover:bg-slate-600 px-3 py-1 rounded text-sm"
                            >
                              Cancel
                            </button>
                          </div>
                        </div>
                      ) : (
                        <div
                          className="text-lg mb-3 cursor-pointer hover:text-emerald-400 transition-colors"
                          onClick={() => {
                            setEditingField({ section: field.section, field: field.field });
                            setEditValue(field.value || '');
                          }}
                        >
                          {field.value || <span className="text-slate-500 italic">Not set</span>}
                        </div>
                      )}

                      {/* Metadata */}
                      <div className="text-xs text-slate-500 space-y-1">
                        {field.source && (
                          <div>
                            Source: <span className="text-slate-400">{field.source.file}</span>
                            {field.source.location && (
                              <span className="text-slate-500"> @ {field.source.location}</span>
                            )}
                          </div>
                        )}
                        {field.derived_from_policy && (
                          <div className="text-blue-400">Derived from firm policy</div>
                        )}
                        {field.user_edited && (
                          <div className="text-emerald-400">User edited</div>
                        )}
                        {field.reasoning && (
                          <div className="mt-2 text-slate-400 italic">{field.reasoning}</div>
                        )}
                        {field.conflicts.length > 0 && (
                          <div className="mt-2 text-amber-400">
                            Conflicts:{' '}
                            {field.conflicts.map((c) => `${c.source}: ${c.value}`).join(', ')}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          ))}
        </div>

        {/* Preview panel */}
        <div className="w-1/2 overflow-y-auto bg-slate-900/50">
          <div className="sticky top-0 bg-slate-900 border-b border-slate-800 px-6 py-3">
            <h2 className="text-lg font-medium text-slate-200">Document Preview</h2>
          </div>
          <div className="p-6 prose prose-invert prose-slate max-w-none">
            <ReactMarkdown>{previewMarkdown}</ReactMarkdown>
          </div>
        </div>
      </div>
    </div>
  );
}
