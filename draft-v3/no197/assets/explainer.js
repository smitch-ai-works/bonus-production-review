// 本人撮影の16:9動画を受領したら、nullを {src:"assets/creator-explainer.mp4",poster:"assets/creator-explainer.jpg"} に変更します。
const BONUS_EXPLAINER = null;
if (BONUS_EXPLAINER && BONUS_EXPLAINER.src) {
  const section = document.createElement('section'); section.className='explainer';
  const player=document.createElement('video'); player.controls=true; player.playsInline=true; player.preload='metadata';
  player.src=BONUS_EXPLAINER.src; player.setAttribute('aria-label','すみっちの使い方解説');
  if(BONUS_EXPLAINER.poster) player.poster=BONUS_EXPLAINER.poster;
  section.appendChild(player); document.getElementById('explainer-root').appendChild(section);
}
