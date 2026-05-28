(function () {
 /*THIS FILE NEEDES TO BE STUDIED AND IS MADE FOR FUN
 */ 
const bee = document.querySelector(".bee-mascot");

  if (!bee) {
    return;
  }

  const edgePadding = 16;
  let position = { x: 24, y: 120 };
  let start = { ...position };
  let target = { ...position };
  let moveStart = performance.now();
  let moveDuration = 2600;
  let pauseUntil = 0;
  let animationFrameId = 0;
  let lastFaceDirection = 1;

  const randomBetween = (min, max) => Math.random() * (max - min) + min;
  const easeInOutSine = (time) => -(Math.cos(Math.PI * time) - 1) / 2;

  function getBounds() {
    const beeBox = bee.getBoundingClientRect();
    return {
      maxX: Math.max(edgePadding, window.innerWidth - beeBox.width - edgePadding),
      maxY: Math.max(edgePadding, window.innerHeight - beeBox.height - edgePadding),
    };
  }

  function clampToScreen(point) {
    const bounds = getBounds();
    return {
      x: Math.min(Math.max(edgePadding, point.x), bounds.maxX),
      y: Math.min(Math.max(edgePadding, point.y), bounds.maxY),
    };
  }

  function chooseTarget(startTime = performance.now()) {
    const bounds = getBounds();
    start = { ...position };
    target = {
      x: randomBetween(edgePadding, bounds.maxX),
      y: randomBetween(edgePadding, bounds.maxY),
    };

    const distance = Math.hypot(target.x - start.x, target.y - start.y);
    moveDuration = Math.min(5200, Math.max(1800, distance * randomBetween(9, 14)));
    moveStart = startTime;

    const direction = target.x >= start.x ? -1 : 1;
    lastFaceDirection = direction;
    bee.style.setProperty("--bee-face", direction);
  }

  function render(now) {
    if (now < pauseUntil) {
      animationFrameId = requestAnimationFrame(render);
      return;
    }

    const progress = Math.min((now - moveStart) / moveDuration, 1);
    const eased = easeInOutSine(progress);
    const wave = Math.sin(progress * Math.PI * 2);

    position = clampToScreen({
      x: start.x + (target.x - start.x) * eased,
      y: start.y + (target.y - start.y) * eased + wave * 10,
    });

    const travelAngle = Math.atan2(target.y - start.y, target.x - start.x);
    const tilt = Math.sin(progress * Math.PI) * 10 * lastFaceDirection;
    const driftTilt = Math.sin(travelAngle) * 4;

    bee.style.setProperty("--bee-x", `${position.x}px`);
    bee.style.setProperty("--bee-y", `${position.y}px`);
    bee.style.setProperty("--bee-tilt", `${tilt + driftTilt}deg`);

    if (progress >= 1) {
      position = clampToScreen(target);
      bee.style.setProperty("--bee-x", `${position.x}px`);
      bee.style.setProperty("--bee-y", `${position.y}px`);
      bee.style.setProperty("--bee-tilt", "0deg");
      pauseUntil = now + randomBetween(350, 1200);
      chooseTarget(pauseUntil);
    }

    animationFrameId = requestAnimationFrame(render);
  }

  function placeBeeOnScreen() {
    position = clampToScreen(position);
    start = { ...position };
    target = { ...position };
    bee.style.setProperty("--bee-x", `${position.x}px`);
    bee.style.setProperty("--bee-y", `${position.y}px`);
  }

  window.addEventListener("resize", placeBeeOnScreen);

  placeBeeOnScreen();
  chooseTarget();
  animationFrameId = requestAnimationFrame(render);

  window.addEventListener("pagehide", () => {
    cancelAnimationFrame(animationFrameId);
  });
})();
