// theme/field.js — live contour field (WebGL2)
// Height field = sum of smooth travelling waves (no grid => no rectangles); iso-lines are drawn with an
// analytic gradient so the line width is exactly constant. Waves drift and slowly morph.
// Usage: <canvas class="field" data-line="255,255,255" data-alpha="0.5"></canvas>
function rng(a){return()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}

const FIELD=(()=>{
  const NWAVE=12, rr=rng(5), WV=[], AM=[];
  for(let n=0;n<NWAVE;n++){
    const ang=rr()*Math.PI*2, kk=Math.exp(Math.log(1.1)+rr()*(Math.log(5.2)-Math.log(1.1)));
    const kx=Math.cos(ang)*kk, ky=Math.sin(ang)*kk;
    WV.push(kx,ky,kx*.045+ky*.02+(rr()-.5)*.09,rr()*6.283);   // k, omega (drift + morph), phase
    AM.push(1/Math.pow(kk,1.05));
  }
  const asum=AM.reduce((x,y)=>x+y,0); for(let n=0;n<NWAVE;n++) AM[n]/=asum;
  const FRAG=`#version 300 es
precision highp float;in vec2 uv;out vec4 o;
uniform float t;uniform vec3 col;uniform float alpha;uniform vec4 W[${NWAVE}];uniform float A[${NWAVE}];
const float S=2.6;       // size of the terrain features
const float N=15.0;      // iso-lines per unit of height
void main(){
  vec2 q=vec2(uv.x*1.7778,uv.y)*S;
  float f=0.;vec2 g=vec2(0.);
  for(int i=0;i<${NWAVE};i++){
    float ph=dot(W[i].xy,q)+W[i].z*t+W[i].w;
    f+=A[i]*sin(ph); g+=A[i]*cos(ph)*W[i].xy; }
  f*=N; g*=N;
  float d=abs(fract(f)-.5)/max(length(g)*(S/720.),1e-3);   // distance to the iso-line, in pixels
  float line=1.-smoothstep(.55,1.45,d);
  float m=smoothstep(.12,1.0,uv.x*.95+(1.-uv.y)*.5-.3);    // fades towards the top-left
  float a=line*m*alpha;
  o=vec4(col*a,a);}`;
  return function make(cv){
    const gl=cv.getContext('webgl2',{premultipliedAlpha:true,alpha:true}); if(!gl) return null;
    cv.width=1280;cv.height=720;
    const sh=(t,src)=>{const o=gl.createShader(t);gl.shaderSource(o,src);gl.compileShader(o);
      if(!gl.getShaderParameter(o,gl.COMPILE_STATUS))console.error(gl.getShaderInfoLog(o));return o};
    const pr=gl.createProgram();
    gl.attachShader(pr,sh(gl.VERTEX_SHADER,`#version 300 es
in vec2 p;out vec2 uv;void main(){uv=p*.5+.5;gl_Position=vec4(p,0,1);}`));
    gl.attachShader(pr,sh(gl.FRAGMENT_SHADER,FRAG));
    gl.linkProgram(pr);gl.useProgram(pr);
    const b=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,b);
    gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,1,1]),gl.STATIC_DRAW);
    const loc=gl.getAttribLocation(pr,'p');gl.enableVertexAttribArray(loc);gl.vertexAttribPointer(loc,2,gl.FLOAT,false,0,0);
    const [r,g,bl]=(cv.dataset.line||'255,255,255').split(',').map(Number);
    gl.uniform3f(gl.getUniformLocation(pr,'col'),r/255,g/255,bl/255);
    gl.uniform1f(gl.getUniformLocation(pr,'alpha'),parseFloat(cv.dataset.alpha||'.5'));
    gl.uniform4fv(gl.getUniformLocation(pr,'W'),new Float32Array(WV));
    gl.uniform1fv(gl.getUniformLocation(pr,'A'),new Float32Array(AM));
    const ut=gl.getUniformLocation(pr,'t');
    return {cv,draw:t=>{gl.viewport(0,0,1280,720);gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT);
      gl.uniform1f(ut,t);gl.drawArrays(gl.TRIANGLE_STRIP,0,4)}};
  };
})();
