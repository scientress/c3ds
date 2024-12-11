import videojs from 'video.js';
import 'video.js/dist/video-js.css';

const video_container = document.getElementById('video')
if (video_container !== null) {
  const video_src = video_container.dataset['src']
  const video_type = video_container.dataset['type']
  if (video_src !== undefined && video_type !== undefined) {
    const player = videojs(video_container, {
      controls: false,
      fill: true,
      loop: true,
    })
    player.src({ src: video_src, type: video_type})
    player.play()
  }
}