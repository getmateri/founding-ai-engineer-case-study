const API_BASE = '/api';

export interface DataSource {
  name: string;
  type: string;
  size: number;
  path: string;
}

export interface DataSourcesResponse {
  sources: DataSource[];
  document_types: string[];
}

export interface StartGenerationResponse {
  session_id: string;
  status: string;
}

export interface GenerationStatusResponse {
  session_id: string;
  status: 'loading' | 'extracting' | 'complete' | 'error';
  progress: string;
  current_section?: string;
  sections_complete: number;
  sections_total: number;
  term_sheet?: TermSheet;
  preview_markdown?: string;
  error?: string;
}

export interface TermSheet {
  document_type: string;
  extracted_at: string;
  sections: {
    [sectionName: string]: {
      [fieldName: string]: FieldData;
    };
  };
}

export interface FieldData {
  value: string | null;
  source: { file: string; location: string } | null;
  confidence: number;
  conflicts: Array<{ source: string; value: string; confidence: number }>;
  found: boolean;
  derived_from_policy: boolean;
  user_edited: boolean;
  reasoning?: string;
}

export interface UpdateFieldResponse {
  success: boolean;
  message: string;
  term_sheet?: TermSheet;
  preview_markdown?: string;
}

export interface FinalizeResponse {
  success: boolean;
  message: string;
  markdown?: string;
  outputs?: { [key: string]: string };
}

// Get available data sources
export async function getDataSources(): Promise<DataSourcesResponse> {
  const res = await fetch(`${API_BASE}/data-sources`);
  if (!res.ok) throw new Error('Failed to get data sources');
  return res.json();
}

// Start generation process
export async function startGeneration(documentType: string): Promise<StartGenerationResponse> {
  const res = await fetch(`${API_BASE}/generate/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ document_type: documentType }),
  });
  if (!res.ok) throw new Error('Failed to start generation');
  return res.json();
}

// Run the generation (blocking call)
export async function runGeneration(sessionId: string): Promise<GenerationStatusResponse> {
  const res = await fetch(`${API_BASE}/generate/run/${sessionId}`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Generation failed');
  return res.json();
}

// Get generation status
export async function getGenerationStatus(sessionId: string): Promise<GenerationStatusResponse> {
  const res = await fetch(`${API_BASE}/generate/status/${sessionId}`);
  if (!res.ok) throw new Error('Failed to get status');
  return res.json();
}

// Update a field
export async function updateField(
  sessionId: string,
  section: string,
  field: string,
  value: string,
  reason?: string
): Promise<UpdateFieldResponse> {
  const res = await fetch(`${API_BASE}/update-field`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, section, field, value, reason }),
  });
  if (!res.ok) throw new Error('Failed to update field');
  return res.json();
}

// Finalize document
export async function finalizeDocument(sessionId: string): Promise<FinalizeResponse> {
  const res = await fetch(`${API_BASE}/finalize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId }),
  });
  if (!res.ok) throw new Error('Failed to finalize');
  return res.json();
}

// Format file size
export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
