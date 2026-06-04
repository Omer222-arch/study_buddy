export const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? '/api';

export interface IngestResponse {
  file_name: string;
  ingested_chunks: number;
  inserted_ids: string[];
}

export interface ChatResponse {
  query: string;
  answer: string;
  retrieved_documents: string[];
  steps_taken: string[];
}

export async function ingestPdf(file: File): Promise<IngestResponse> {
  const form = new FormData();
  form.append('file', file, file.name);

  const response = await fetch(`${apiBaseUrl}/ingest`, {
    method: 'POST',
    body: form,
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || 'Failed to ingest PDF.');
  }

  return response.json();
}

export async function askChat(query: string, top_k: number): Promise<ChatResponse> {
  const response = await fetch(`${apiBaseUrl}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query, top_k }),
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || 'Chat request failed.');
  }

  return response.json();
}
