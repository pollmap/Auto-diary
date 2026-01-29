/**
 * 시황 브리핑 테이블 색상 자동 적용
 * 상승(+): 초록색, 하락(-): 빨간색
 */
document.addEventListener('DOMContentLoaded', function() {
  // 모든 테이블 셀 검사
  const cells = document.querySelectorAll('td');

  cells.forEach(cell => {
    const text = cell.textContent.trim();

    // +로 시작하는 퍼센트 (상승)
    if (/^\+\d/.test(text) || /^\+0\./.test(text)) {
      cell.style.color = '#00b894';
      cell.style.fontWeight = '600';
    }
    // -로 시작하는 퍼센트 (하락)
    else if (/^-\d/.test(text) || /^-0\./.test(text)) {
      cell.style.color = '#d63031';
      cell.style.fontWeight = '600';
    }
  });

  // Fear & Greed 지수 색상
  const content = document.querySelector('.post-content');
  if (content) {
    content.innerHTML = content.innerHTML
      .replace(/🟢/g, '<span style="color:#00b894;font-size:1.2em;">🟢</span>')
      .replace(/🔴/g, '<span style="color:#d63031;font-size:1.2em;">🔴</span>')
      .replace(/🟡/g, '<span style="color:#fdcb6e;font-size:1.2em;">🟡</span>');
  }
});
