import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface MoveStats {
  uci: string;
  san: string;
  white: number;
  draws: number;
  black: number;
  average_rating: number | null;
  total_games: number;
}

export interface MovesResponse {
  fen: string;
  total_games: number;
  moves: MoveStats[];
}

export interface EvaluationResponse {
  fen: string;
  evaluation_type: string;
  evaluation_value: number;
  best_move_uci: string;
  best_move_san: string;
  depth: number;
}

export interface SearchResult {
  title: string;
  chunk: string;
  source: string;
  opening_name: string;
  score: number;
}

export interface VectorSearchResponse {
  query: string;
  results: SearchResult[];
}

export interface VideoResult {
  video_id: string;
  title: string;
  description: string;
  channel: string;
  published_at: string;
  thumbnail: string;
  url: string;
  embed_url: string;
  duration: string;
  view_count: number;
}

export interface VideosResponse {
  opening: string;
  count: number;
  videos: VideoResult[];
}

export interface AgentAnalysis {
  fen: string;
  response: string;
  tools_used: string[];
  opening_name: string;
}

@Injectable({
  providedIn: 'root'
})
export class ChessApiService {
  private baseUrl = 'http://localhost:8000/api/v1';

  constructor(private http: HttpClient) {}

  getMoves(fen: string): Observable<MovesResponse> {
    const params = new HttpParams().set('fen', fen);
    return this.http.get<MovesResponse>(`${this.baseUrl}/moves`, { params });
  }

  evaluate(fen: string): Observable<EvaluationResponse> {
    const params = new HttpParams().set('fen', fen);
    return this.http.get<EvaluationResponse>(`${this.baseUrl}/evaluate`, { params });
  }

  vectorSearch(query: string, topK: number = 3): Observable<VectorSearchResponse> {
    const params = new HttpParams()
      .set('query', query)
      .set('top_k', topK.toString());
    return this.http.get<VectorSearchResponse>(`${this.baseUrl}/vector-search`, { params });
  }

  getVideos(opening: string, maxResults: number = 3): Observable<VideosResponse> {
    const params = new HttpParams().set('max_results', maxResults.toString());
    return this.http.get<VideosResponse>(`${this.baseUrl}/videos/${encodeURIComponent(opening)}`, { params });
  }

  analyzePosition(fen: string): Observable<AgentAnalysis> {
    const params = new HttpParams().set('fen', fen);
    return this.http.post<AgentAnalysis>(`${this.baseUrl}/agent/analyze`, null, { params });
  }
}
