import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  MoveStats,
  EvaluationResponse,
  SearchResult,
} from '../../services/chess-api.service';

@Component({
  selector: 'app-recommendations',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './recommendations.component.html',
  styleUrl: './recommendations.component.scss',
})
export class RecommendationsComponent {
  @Input() moves: MoveStats[] = [];
  @Input() evaluation: EvaluationResponse | null = null;
  @Input() searchResults: SearchResult[] = [];
  @Input() loadingMoves = false;
  @Input() loadingEval = false;
  @Input() loadingSearch = false;
  @Input() openingName = '';
  @Input() error = '';

  getEvalDisplay(): string {
    if (!this.evaluation) return '';
    if (this.evaluation.evaluation_type === 'mate') {
      return `Mat en ${this.evaluation.evaluation_value}`;
    }
    const cp = this.evaluation.evaluation_value / 100;
    return cp > 0 ? `+${cp.toFixed(2)}` : cp.toFixed(2);
  }

  getEvalClass(): string {
    if (!this.evaluation) return '';
    if (this.evaluation.evaluation_type === 'mate') {
      return this.evaluation.evaluation_value > 0 ? 'eval-white' : 'eval-black';
    }
    return this.evaluation.evaluation_value > 0 ? 'eval-white' : 'eval-black';
  }

  getWinRate(move: MoveStats): { white: number; draw: number; black: number } {
    const total = move.total_games || 1;
    return {
      white: Math.round((move.white / total) * 100),
      draw: Math.round((move.draws / total) * 100),
      black: Math.round((move.black / total) * 100),
    };
  }
}
