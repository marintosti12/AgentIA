import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { VideoResult } from '../../services/chess-api.service';

@Component({
  selector: 'app-video-panel',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './video-panel.component.html',
  styleUrl: './video-panel.component.scss',
})
export class VideoPanelComponent {
  @Input() videos: VideoResult[] = [];
  @Input() loading = false;
  @Input() openingName = '';

  selectedVideo: VideoResult | null = null;

  constructor(private sanitizer: DomSanitizer) {}

  getEmbedUrl(video: VideoResult): SafeResourceUrl {
    return this.sanitizer.bypassSecurityTrustResourceUrl(video.embed_url);
  }

  selectVideo(video: VideoResult): void {
    this.selectedVideo = this.selectedVideo?.video_id === video.video_id ? null : video;
  }

  formatDuration(iso: string): string {
    if (!iso) return '';
    const match = iso.match(/PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/);
    if (!match) return iso;
    const h = match[1] ? `${match[1]}h` : '';
    const m = match[2] ? `${match[2]}m` : '0m';
    const s = match[3] ? `${match[3]}s` : '';
    return `${h}${m}${s}`;
  }

  formatViews(count: number): string {
    if (count >= 1_000_000) return `${(count / 1_000_000).toFixed(1)}M vues`;
    if (count >= 1_000) return `${(count / 1_000).toFixed(0)}K vues`;
    return `${count} vues`;
  }
}
