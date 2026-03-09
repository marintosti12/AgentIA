import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChessboardComponent } from './components/chessboard/chessboard.component';
import { RecommendationsComponent } from './components/recommendations/recommendations.component';
import { VideoPanelComponent } from './components/video-panel/video-panel.component';
import {
  ChessApiService,
  MoveStats,
  EvaluationResponse,
  SearchResult,
  VideoResult,
} from './services/chess-api.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    ChessboardComponent,
    RecommendationsComponent,
    VideoPanelComponent,
  ],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App {
  moves: MoveStats[] = [];
  evaluation: EvaluationResponse | null = null;
  searchResults: SearchResult[] = [];
  videos: VideoResult[] = [];
  openingName = '';
  error = '';

  loadingMoves = false;
  loadingEval = false;
  loadingSearch = false;
  loadingVideos = false;

  private lastOpeningName = '';

  constructor(private chessApi: ChessApiService) {}

  onFenChange(fen: string): void {
    // ngx-chess-board may return only the piece placement part
    // Complete with default suffix if needed
    if (fen && !fen.includes(' ')) {
      fen = fen + ' w KQkq - 0 1';
    }
    this.error = '';
    this.fetchMoves(fen);
    this.fetchEvaluation(fen);
    this.fetchOpeningContext(fen);
  }

  private fetchMoves(fen: string): void {
    this.loadingMoves = true;
    this.chessApi.getMoves(fen).subscribe({
      next: (res) => {
        this.moves = res.moves;
        this.loadingMoves = false;
      },
      error: () => {
        this.moves = [];
        this.loadingMoves = false;
      },
    });
  }

  private fetchEvaluation(fen: string): void {
    this.loadingEval = true;
    this.chessApi.evaluate(fen).subscribe({
      next: (res) => {
        this.evaluation = res;
        this.loadingEval = false;
      },
      error: () => {
        this.evaluation = null;
        this.loadingEval = false;
      },
    });
  }

  private fetchOpeningContext(fen: string): void {
    this.loadingSearch = true;
    const query = `position echecs ${fen}`;
    this.chessApi.vectorSearch(query, 2).subscribe({
      next: (res) => {
        this.searchResults = res.results;
        this.loadingSearch = false;

        const detectedOpening = res.results.length > 0 ? res.results[0].opening_name : '';
        if (detectedOpening && detectedOpening !== this.lastOpeningName) {
          this.openingName = detectedOpening;
          this.lastOpeningName = detectedOpening;
          this.fetchVideos(detectedOpening);
        }
      },
      error: () => {
        this.searchResults = [];
        this.loadingSearch = false;
      },
    });
  }

  private fetchVideos(opening: string): void {
    this.loadingVideos = true;
    this.chessApi.getVideos(opening, 3).subscribe({
      next: (res) => {
        this.videos = res.videos;
        this.loadingVideos = false;
      },
      error: () => {
        this.videos = [];
        this.loadingVideos = false;
      },
    });
  }
}
