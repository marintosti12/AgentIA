import { Component, ViewChild, Output, EventEmitter, AfterViewInit } from '@angular/core';
import { NgxChessBoardModule, NgxChessBoardView } from 'ngx-chess-board';

@Component({
  selector: 'app-chessboard',
  standalone: true,
  imports: [NgxChessBoardModule],
  templateUrl: './chessboard.component.html',
  styleUrl: './chessboard.component.scss'
})
export class ChessboardComponent implements AfterViewInit {
  @ViewChild('board') board!: NgxChessBoardView;
  @Output() moveChange = new EventEmitter<string>();

  currentFen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';

  ngAfterViewInit(): void {
    setTimeout(() => {
      this.emitFen();
    }, 100);
  }

  onMoveChange(event: any): void {
    setTimeout(() => {
      this.emitFen();
    }, 50);
  }

  private emitFen(): void {
    if (this.board) {
      this.currentFen = this.board.getFEN();
      this.moveChange.emit(this.currentFen);
    }
  }

  reset(): void {
    this.board.reset();
    setTimeout(() => this.emitFen(), 50);
  }

  reverse(): void {
    this.board.reverse();
  }

  undo(): void {
    this.board.undo();
    setTimeout(() => this.emitFen(), 50);
  }
}
