/** Original teaching geometry. No target code or OS calls. All sizes carry explicit units. */
function finite(value, name) {
  if (!Number.isFinite(value)) throw new TypeError(`${name} must be finite`);
  return value;
}
function positive(value, name) {
  if (finite(value, name) <= 0) throw new RangeError(`${name} must be positive`);
  return value;
}
function point(point) {
  if (!Array.isArray(point) || point.length !== 2) throw new TypeError('point must be [x,y]');
  for (let i = 0; i < point.length; i++) finite(point[i], `point[${i}]`);
  return point;
}
function frameSize(frame) {
  return [positive(frame.frameWidth ?? frame.imageWidth, 'frameWidth'),
    positive(frame.frameHeight ?? frame.imageHeight, 'frameHeight')];
}
function requireFresh(frame, expectedCaptureId) {
  if (!frame || !expectedCaptureId || frame.captureId !== expectedCaptureId)
    throw new Error('A matching capture identity is required');
}
/** Returns executor display-space coordinates, not presumed physical pixels. */
export function mapDisplayPoint(input, frame, expectedCaptureId, mode = 'frame-pixels') {
  requireFresh(frame, expectedCaptureId);
  const [x, y] = point(input);
  const [fw, fh] = frameSize(frame);
  const dw = positive(frame.displayWidth, 'displayWidth');
  const dh = positive(frame.displayHeight, 'displayHeight');
  const ox = finite(frame.originX, 'originX'), oy = finite(frame.originY, 'originY');
  if (!['frame-pixels', 'percent-0-100'].includes(mode)) throw new RangeError('Unknown coordinate mode');
  const [mx, my] = mode === 'frame-pixels' ? [fw, fh] : [100, 100];
  if (x < 0 || y < 0 || x > mx || y > my) throw new RangeError('Point lies outside its declared frame');
  const localX = Math.min(Math.round((x / mx) * dw), Math.max(dw - 1, 0));
  const localY = Math.min(Math.round((y / my) * dh), Math.max(dh - 1, 0));
  return {x: ox + localX, y: oy + localY, displayId: frame.displayId};
}
/** Deliberately strict educational policy: reject invalid points instead of silently clamping. */
export function mapWindowPoint(input, frame, expectedCaptureId) {
  requireFresh(frame, expectedCaptureId);
  const [x, y] = point(input), [fw, fh] = frameSize(frame);
  const width = positive(frame.windowWidth, 'windowWidth');
  const height = positive(frame.windowHeight, 'windowHeight');
  if (x < 0 || y < 0 || x > fw || y > fh) throw new RangeError('Window point is outside its frame');
  return {x: (x / fw) * width, y: (y / fh) * height, windowId: frame.windowId};
}
export function apply(matrix, input) {
  if (!Array.isArray(matrix) || matrix.length !== 6) throw new TypeError('Expected affine matrix [a,b,c,d,e,f]');
  for (let i = 0; i < matrix.length; i++) finite(matrix[i], `matrix[${i}]`);
  const [x, y] = point(input), [a,b,c,d,e,f] = matrix;
  return [a*x+c*y+e, b*x+d*y+f];
}
/** compose(outer, inner) applies inner first. */
export function compose(outer, inner) {
  apply(outer, [0,0]); apply(inner, [0,0]);
  const [a,b,c,d,e,f] = outer, [g,h,i,j,k,l] = inner;
  return [a*g+c*h,b*g+d*h,a*i+c*j,b*i+d*j,a*k+c*l+e,b*k+d*l+f];
}
export function invert(matrix) {
  apply(matrix, [0,0]);
  const [a,b,c,d,e,f] = matrix, det = a*d-b*c;
  if (!Number.isFinite(det) || det === 0) throw new RangeError('Singular or unrepresentable transform');
  const inverse = [d/det,-b/det,-c/det,a/det,(c*f-d*e)/det,(b*e-a*f)/det];
  if (!inverse.every(Number.isFinite)) throw new RangeError('Unrepresentable inverse');
  return inverse;
}
export function rectBounds(rect, matrix) {
  if (!Array.isArray(rect) || rect.length !== 4) throw new TypeError('Expected [left,bottom,right,top]');
  for (let i = 0; i < rect.length; i++) finite(rect[i], `rect[${i}]`);
  const [x0,y0,x1,y1] = rect;
  const corners = [[x0,y0],[x0,y1],[x1,y0],[x1,y1]].map(p => apply(matrix,p));
  const xs = corners.map(p=>p[0]), ys = corners.map(p=>p[1]);
  return [Math.min(...xs),Math.min(...ys),Math.max(...xs),Math.max(...ys)];
}
/** Standard PDF bottom-left user space -> top-left CSS viewport. Original derivation. */
export function pdfViewport({viewBox, zoom=1, userUnit=1, rotation=0, offsetX=0, offsetY=0}) {
  if (!Array.isArray(viewBox) || viewBox.length !== 4) throw new TypeError('Expected a viewBox');
  const [left,bottom,right,top] = viewBox;
  for (let i = 0; i < viewBox.length; i++) finite(viewBox[i], `viewBox[${i}]`);
  positive(right-left,'viewBox width'); positive(top-bottom,'viewBox height');
  positive(zoom,'zoom'); positive(userUnit,'userUnit'); finite(rotation,'rotation');
  finite(offsetX,'offsetX'); finite(offsetY,'offsetY');
  if (rotation % 90 !== 0) throw new RangeError('PDF viewport rotation must be a multiple of 90');
  const turn = ((rotation % 360)+360)%360;
  const [cos,sin] = {0:[1,0],90:[0,1],180:[-1,0],270:[0,-1]}[turn];
  const scale=positive(zoom*userUnit,'effective scale'), linear=[scale*cos,scale*sin,scale*sin,-scale*cos,0,0];
  const [x0,y0,x1,y1]=rectBounds(viewBox,linear);
  const matrix=[...linear.slice(0,4),offsetX-x0,offsetY-y0];
  return {matrix,width:x1-x0,height:y1-y0,rotation:turn};
}
/** CSS event positions stay CSS; DPR is added only for a backing-store output. */
export function canvasTransform(viewportMatrix, devicePixelRatio) {
  positive(devicePixelRatio,'devicePixelRatio');
  return compose([devicePixelRatio,0,0,devicePixelRatio,0,0],viewportMatrix);
}
