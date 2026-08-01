/*!
# Third-party notices

The ChoreFlow dashboard card bundles the following third-party software.

## Lit

Source: <https://github.com/lit/lit>

BSD 3-Clause License

Copyright (c) 2017 Google LLC. All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

## custom-card-helpers

Source: <https://github.com/custom-cards/custom-card-helpers>

MIT License

Copyright (c) 2019 Custom cards for Home Assistant

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/
function e(e,t,i,s){var o,r=arguments.length,n=r<3?t:null===s?s=Object.getOwnPropertyDescriptor(t,i):s;if("object"==typeof Reflect&&"function"==typeof Reflect.decorate)n=Reflect.decorate(e,t,i,s);else for(var a=e.length-1;a>=0;a--)(o=e[a])&&(n=(r<3?o(n):r>3?o(t,i,n):o(t,i))||n);return r>3&&n&&Object.defineProperty(t,i,n),n}"function"==typeof SuppressedError&&SuppressedError;const t=globalThis,i=t.ShadowRoot&&(void 0===t.ShadyCSS||t.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,s=Symbol(),o=new WeakMap;let r=class{constructor(e,t,i){if(this._$cssResult$=!0,i!==s)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t}get styleSheet(){let e=this.o;const t=this.t;if(i&&void 0===e){const i=void 0!==t&&1===t.length;i&&(e=o.get(t)),void 0===e&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),i&&o.set(t,e))}return e}toString(){return this.cssText}};const n=(e,...t)=>{const i=1===e.length?e[0]:t.reduce((t,i,s)=>t+(e=>{if(!0===e._$cssResult$)return e.cssText;if("number"==typeof e)return e;throw Error("Value passed to 'css' function must be a 'css' function result: "+e+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+e[s+1],e[0]);return new r(i,e,s)},a=i?e=>e:e=>e instanceof CSSStyleSheet?(e=>{let t="";for(const i of e.cssRules)t+=i.cssText;return(e=>new r("string"==typeof e?e:e+"",void 0,s))(t)})(e):e,{is:l,defineProperty:c,getOwnPropertyDescriptor:d,getOwnPropertyNames:h,getOwnPropertySymbols:p,getPrototypeOf:u}=Object,_=globalThis,g=_.trustedTypes,m=g?g.emptyScript:"",f=_.reactiveElementPolyfillSupport,v=(e,t)=>e,y={toAttribute(e,t){switch(t){case Boolean:e=e?m:null;break;case Object:case Array:e=null==e?e:JSON.stringify(e)}return e},fromAttribute(e,t){let i=e;switch(t){case Boolean:i=null!==e;break;case Number:i=null===e?null:Number(e);break;case Object:case Array:try{i=JSON.parse(e)}catch(e){i=null}}return i}},b=(e,t)=>!l(e,t),x={attribute:!0,type:String,converter:y,reflect:!1,useDefault:!1,hasChanged:b};Symbol.metadata??=Symbol("metadata"),_.litPropertyMetadata??=new WeakMap;let k=class extends HTMLElement{static addInitializer(e){this._$Ei(),(this.l??=[]).push(e)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(e,t=x){if(t.state&&(t.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(e)&&((t=Object.create(t)).wrapped=!0),this.elementProperties.set(e,t),!t.noAccessor){const i=Symbol(),s=this.getPropertyDescriptor(e,i,t);void 0!==s&&c(this.prototype,e,s)}}static getPropertyDescriptor(e,t,i){const{get:s,set:o}=d(this.prototype,e)??{get(){return this[t]},set(e){this[t]=e}};return{get:s,set(t){const r=s?.call(this);o?.call(this,t),this.requestUpdate(e,r,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)??x}static _$Ei(){if(this.hasOwnProperty(v("elementProperties")))return;const e=u(this);e.finalize(),void 0!==e.l&&(this.l=[...e.l]),this.elementProperties=new Map(e.elementProperties)}static finalize(){if(this.hasOwnProperty(v("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(v("properties"))){const e=this.properties,t=[...h(e),...p(e)];for(const i of t)this.createProperty(i,e[i])}const e=this[Symbol.metadata];if(null!==e){const t=litPropertyMetadata.get(e);if(void 0!==t)for(const[e,i]of t)this.elementProperties.set(e,i)}this._$Eh=new Map;for(const[e,t]of this.elementProperties){const i=this._$Eu(e,t);void 0!==i&&this._$Eh.set(i,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(e){const t=[];if(Array.isArray(e)){const i=new Set(e.flat(1/0).reverse());for(const e of i)t.unshift(a(e))}else void 0!==e&&t.push(a(e));return t}static _$Eu(e,t){const i=t.attribute;return!1===i?void 0:"string"==typeof i?i:"string"==typeof e?e.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(e=>this.enableUpdating=e),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(e=>e(this))}addController(e){(this._$EO??=new Set).add(e),void 0!==this.renderRoot&&this.isConnected&&e.hostConnected?.()}removeController(e){this._$EO?.delete(e)}_$E_(){const e=new Map,t=this.constructor.elementProperties;for(const i of t.keys())this.hasOwnProperty(i)&&(e.set(i,this[i]),delete this[i]);e.size>0&&(this._$Ep=e)}createRenderRoot(){const e=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return((e,s)=>{if(i)e.adoptedStyleSheets=s.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(const i of s){const s=document.createElement("style"),o=t.litNonce;void 0!==o&&s.setAttribute("nonce",o),s.textContent=i.cssText,e.appendChild(s)}})(e,this.constructor.elementStyles),e}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(e=>e.hostConnected?.())}enableUpdating(e){}disconnectedCallback(){this._$EO?.forEach(e=>e.hostDisconnected?.())}attributeChangedCallback(e,t,i){this._$AK(e,i)}_$ET(e,t){const i=this.constructor.elementProperties.get(e),s=this.constructor._$Eu(e,i);if(void 0!==s&&!0===i.reflect){const o=(void 0!==i.converter?.toAttribute?i.converter:y).toAttribute(t,i.type);this._$Em=e,null==o?this.removeAttribute(s):this.setAttribute(s,o),this._$Em=null}}_$AK(e,t){const i=this.constructor,s=i._$Eh.get(e);if(void 0!==s&&this._$Em!==s){const e=i.getPropertyOptions(s),o="function"==typeof e.converter?{fromAttribute:e.converter}:void 0!==e.converter?.fromAttribute?e.converter:y;this._$Em=s;const r=o.fromAttribute(t,e.type);this[s]=r??this._$Ej?.get(s)??r,this._$Em=null}}requestUpdate(e,t,i,s=!1,o){if(void 0!==e){const r=this.constructor;if(!1===s&&(o=this[e]),i??=r.getPropertyOptions(e),!((i.hasChanged??b)(o,t)||i.useDefault&&i.reflect&&o===this._$Ej?.get(e)&&!this.hasAttribute(r._$Eu(e,i))))return;this.C(e,t,i)}!1===this.isUpdatePending&&(this._$ES=this._$EP())}C(e,t,{useDefault:i,reflect:s,wrapped:o},r){i&&!(this._$Ej??=new Map).has(e)&&(this._$Ej.set(e,r??t??this[e]),!0!==o||void 0!==r)||(this._$AL.has(e)||(this.hasUpdated||i||(t=void 0),this._$AL.set(e,t)),!0===s&&this._$Em!==e&&(this._$Eq??=new Set).add(e))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}const e=this.scheduleUpdate();return null!=e&&await e,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(const[e,t]of this._$Ep)this[e]=t;this._$Ep=void 0}const e=this.constructor.elementProperties;if(e.size>0)for(const[t,i]of e){const{wrapped:e}=i,s=this[t];!0!==e||this._$AL.has(t)||void 0===s||this.C(t,void 0,i,s)}}let e=!1;const t=this._$AL;try{e=this.shouldUpdate(t),e?(this.willUpdate(t),this._$EO?.forEach(e=>e.hostUpdate?.()),this.update(t)):this._$EM()}catch(t){throw e=!1,this._$EM(),t}e&&this._$AE(t)}willUpdate(e){}_$AE(e){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(e){return!0}update(e){this._$Eq&&=this._$Eq.forEach(e=>this._$ET(e,this[e])),this._$EM()}updated(e){}firstUpdated(e){}};k.elementStyles=[],k.shadowRootOptions={mode:"open"},k[v("elementProperties")]=new Map,k[v("finalized")]=new Map,f?.({ReactiveElement:k}),(_.reactiveElementVersions??=[]).push("2.1.2");const $=globalThis,w=e=>e,E=$.trustedTypes,A=E?E.createPolicy("lit-html",{createHTML:e=>e}):void 0,S="$lit$",P=`lit$${Math.random().toFixed(9).slice(2)}$`,T="?"+P,z=`<${T}>`,R=document,F=()=>R.createComment(""),C=e=>null===e||"object"!=typeof e&&"function"!=typeof e,O=Array.isArray,D="[ \t\n\f\r]",M=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,H=/-->/g,N=/>/g,U=RegExp(`>|${D}(?:([^\\s"'>=/]+)(${D}*=${D}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),L=/'/g,j=/"/g,B=/^(?:script|style|textarea|title)$/i,I=(e=>(t,...i)=>({_$litType$:e,strings:t,values:i}))(1),K=Symbol.for("lit-noChange"),W=Symbol.for("lit-nothing"),G=new WeakMap,q=R.createTreeWalker(R,129);function V(e,t){if(!O(e)||!e.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==A?A.createHTML(t):t}const Z=(e,t)=>{const i=e.length-1,s=[];let o,r=2===t?"<svg>":3===t?"<math>":"",n=M;for(let t=0;t<i;t++){const i=e[t];let a,l,c=-1,d=0;for(;d<i.length&&(n.lastIndex=d,l=n.exec(i),null!==l);)d=n.lastIndex,n===M?"!--"===l[1]?n=H:void 0!==l[1]?n=N:void 0!==l[2]?(B.test(l[2])&&(o=RegExp("</"+l[2],"g")),n=U):void 0!==l[3]&&(n=U):n===U?">"===l[0]?(n=o??M,c=-1):void 0===l[1]?c=-2:(c=n.lastIndex-l[2].length,a=l[1],n=void 0===l[3]?U:'"'===l[3]?j:L):n===j||n===L?n=U:n===H||n===N?n=M:(n=U,o=void 0);const h=n===U&&e[t+1].startsWith("/>")?" ":"";r+=n===M?i+z:c>=0?(s.push(a),i.slice(0,c)+S+i.slice(c)+P+h):i+P+(-2===c?t:h)}return[V(e,r+(e[i]||"<?>")+(2===t?"</svg>":3===t?"</math>":"")),s]};class J{constructor({strings:e,_$litType$:t},i){let s;this.parts=[];let o=0,r=0;const n=e.length-1,a=this.parts,[l,c]=Z(e,t);if(this.el=J.createElement(l,i),q.currentNode=this.el.content,2===t||3===t){const e=this.el.content.firstChild;e.replaceWith(...e.childNodes)}for(;null!==(s=q.nextNode())&&a.length<n;){if(1===s.nodeType){if(s.hasAttributes())for(const e of s.getAttributeNames())if(e.endsWith(S)){const t=c[r++],i=s.getAttribute(e).split(P),n=/([.?@])?(.*)/.exec(t);a.push({type:1,index:o,name:n[2],strings:i,ctor:"."===n[1]?te:"?"===n[1]?ie:"@"===n[1]?se:ee}),s.removeAttribute(e)}else e.startsWith(P)&&(a.push({type:6,index:o}),s.removeAttribute(e));if(B.test(s.tagName)){const e=s.textContent.split(P),t=e.length-1;if(t>0){s.textContent=E?E.emptyScript:"";for(let i=0;i<t;i++)s.append(e[i],F()),q.nextNode(),a.push({type:2,index:++o});s.append(e[t],F())}}}else if(8===s.nodeType)if(s.data===T)a.push({type:2,index:o});else{let e=-1;for(;-1!==(e=s.data.indexOf(P,e+1));)a.push({type:7,index:o}),e+=P.length-1}o++}}static createElement(e,t){const i=R.createElement("template");return i.innerHTML=e,i}}function Y(e,t,i=e,s){if(t===K)return t;let o=void 0!==s?i._$Co?.[s]:i._$Cl;const r=C(t)?void 0:t._$litDirective$;return o?.constructor!==r&&(o?._$AO?.(!1),void 0===r?o=void 0:(o=new r(e),o._$AT(e,i,s)),void 0!==s?(i._$Co??=[])[s]=o:i._$Cl=o),void 0!==o&&(t=Y(e,o._$AS(e,t.values),o,s)),t}class Q{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){const{el:{content:t},parts:i}=this._$AD,s=(e?.creationScope??R).importNode(t,!0);q.currentNode=s;let o=q.nextNode(),r=0,n=0,a=i[0];for(;void 0!==a;){if(r===a.index){let t;2===a.type?t=new X(o,o.nextSibling,this,e):1===a.type?t=new a.ctor(o,a.name,a.strings,this,e):6===a.type&&(t=new oe(o,this,e)),this._$AV.push(t),a=i[++n]}r!==a?.index&&(o=q.nextNode(),r++)}return q.currentNode=R,s}p(e){let t=0;for(const i of this._$AV)void 0!==i&&(void 0!==i.strings?(i._$AI(e,i,t),t+=i.strings.length-2):i._$AI(e[t])),t++}}class X{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(e,t,i,s){this.type=2,this._$AH=W,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=i,this.options=s,this._$Cv=s?.isConnected??!0}get parentNode(){let e=this._$AA.parentNode;const t=this._$AM;return void 0!==t&&11===e?.nodeType&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=Y(this,e,t),C(e)?e===W||null==e||""===e?(this._$AH!==W&&this._$AR(),this._$AH=W):e!==this._$AH&&e!==K&&this._(e):void 0!==e._$litType$?this.$(e):void 0!==e.nodeType?this.T(e):(e=>O(e)||"function"==typeof e?.[Symbol.iterator])(e)?this.k(e):this._(e)}O(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}T(e){this._$AH!==e&&(this._$AR(),this._$AH=this.O(e))}_(e){this._$AH!==W&&C(this._$AH)?this._$AA.nextSibling.data=e:this.T(R.createTextNode(e)),this._$AH=e}$(e){const{values:t,_$litType$:i}=e,s="number"==typeof i?this._$AC(e):(void 0===i.el&&(i.el=J.createElement(V(i.h,i.h[0]),this.options)),i);if(this._$AH?._$AD===s)this._$AH.p(t);else{const e=new Q(s,this),i=e.u(this.options);e.p(t),this.T(i),this._$AH=e}}_$AC(e){let t=G.get(e.strings);return void 0===t&&G.set(e.strings,t=new J(e)),t}k(e){O(this._$AH)||(this._$AH=[],this._$AR());const t=this._$AH;let i,s=0;for(const o of e)s===t.length?t.push(i=new X(this.O(F()),this.O(F()),this,this.options)):i=t[s],i._$AI(o),s++;s<t.length&&(this._$AR(i&&i._$AB.nextSibling,s),t.length=s)}_$AR(e=this._$AA.nextSibling,t){for(this._$AP?.(!1,!0,t);e!==this._$AB;){const t=w(e).nextSibling;w(e).remove(),e=t}}setConnected(e){void 0===this._$AM&&(this._$Cv=e,this._$AP?.(e))}}class ee{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(e,t,i,s,o){this.type=1,this._$AH=W,this._$AN=void 0,this.element=e,this.name=t,this._$AM=s,this.options=o,i.length>2||""!==i[0]||""!==i[1]?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=W}_$AI(e,t=this,i,s){const o=this.strings;let r=!1;if(void 0===o)e=Y(this,e,t,0),r=!C(e)||e!==this._$AH&&e!==K,r&&(this._$AH=e);else{const s=e;let n,a;for(e=o[0],n=0;n<o.length-1;n++)a=Y(this,s[i+n],t,n),a===K&&(a=this._$AH[n]),r||=!C(a)||a!==this._$AH[n],a===W?e=W:e!==W&&(e+=(a??"")+o[n+1]),this._$AH[n]=a}r&&!s&&this.j(e)}j(e){e===W?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}}class te extends ee{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===W?void 0:e}}class ie extends ee{constructor(){super(...arguments),this.type=4}j(e){this.element.toggleAttribute(this.name,!!e&&e!==W)}}class se extends ee{constructor(e,t,i,s,o){super(e,t,i,s,o),this.type=5}_$AI(e,t=this){if((e=Y(this,e,t,0)??W)===K)return;const i=this._$AH,s=e===W&&i!==W||e.capture!==i.capture||e.once!==i.once||e.passive!==i.passive,o=e!==W&&(i===W||s);s&&this.element.removeEventListener(this.name,this,i),o&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){"function"==typeof this._$AH?this._$AH.call(this.options?.host??this.element,e):this._$AH.handleEvent(e)}}class oe{constructor(e,t,i){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(e){Y(this,e)}}const re=$.litHtmlPolyfillSupport;re?.(J,X),($.litHtmlVersions??=[]).push("3.3.3");const ne=globalThis;let ae=class extends k{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){const e=super.createRenderRoot();return this.renderOptions.renderBefore??=e.firstChild,e}update(e){const t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=((e,t,i)=>{const s=i?.renderBefore??t;let o=s._$litPart$;if(void 0===o){const e=i?.renderBefore??null;s._$litPart$=o=new X(t.insertBefore(F(),e),e,void 0,i??{})}return o._$AI(e),o})(t,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return K}};ae._$litElement$=!0,ae.finalized=!0,ne.litElementHydrateSupport?.({LitElement:ae});const le=ne.litElementPolyfillSupport;le?.({LitElement:ae}),(ne.litElementVersions??=[]).push("4.2.2");const ce=e=>(t,i)=>{void 0!==i?i.addInitializer(()=>{customElements.define(e,t)}):customElements.define(e,t)},de={attribute:!0,type:String,converter:y,reflect:!1,hasChanged:b},he=(e=de,t,i)=>{const{kind:s,metadata:o}=i;let r=globalThis.litPropertyMetadata.get(o);if(void 0===r&&globalThis.litPropertyMetadata.set(o,r=new Map),"setter"===s&&((e=Object.create(e)).wrapped=!0),r.set(i.name,e),"accessor"===s){const{name:s}=i;return{set(i){const o=t.get.call(this);t.set.call(this,i),this.requestUpdate(s,o,e,!0,i)},init(t){return void 0!==t&&this.C(s,void 0,e,t),t}}}if("setter"===s){const{name:s}=i;return function(i){const o=this[s];t.call(this,i),this.requestUpdate(s,o,e,!0,i)}}throw Error("Unsupported decorator location: "+s)};function pe(e){return(t,i)=>"object"==typeof i?he(e,t,i):((e,t,i)=>{const s=t.hasOwnProperty(i);return t.constructor.createProperty(i,e),s?Object.getOwnPropertyDescriptor(t,i):void 0})(e,t,i)}function ue(e){return pe({...e,state:!0,attribute:!1})}const _e=1;class ge{constructor(e){}get _$AU(){return this._$AM._$AU}_$AT(e,t,i){this._$Ct=e,this._$AM=t,this._$Ci=i}_$AS(e,t){return this.update(e,t)}update(e,t){return this.render(...t)}}const me=(e=>(...t)=>({_$litDirective$:e,values:t}))(class extends ge{constructor(e){if(super(e),e.type!==_e||"class"!==e.name||e.strings?.length>2)throw Error("`classMap()` can only be used in the `class` attribute and must be the only part in the attribute.")}render(e){return" "+Object.keys(e).filter(t=>e[t]).join(" ")+" "}update(e,[t]){if(void 0===this.st){this.st=new Set,void 0!==e.strings&&(this.nt=new Set(e.strings.join(" ").split(/\s/).filter(e=>""!==e)));for(const e in t)t[e]&&!this.nt?.has(e)&&this.st.add(e);return this.render(t)}const i=e.element.classList;for(const e of this.st)e in t||(i.remove(e),this.st.delete(e));for(const e in t){const s=!!t[e];s===this.st.has(e)||this.nt?.has(e)||(s?(i.add(e),this.st.add(e)):(i.remove(e),this.st.delete(e)))}return K}});let fe=class extends ae{setConfig(e){this._config={...e,entities:{...e.entities,open_tasks:e.entities?.open_tasks??""}}}_emit(e){this._config=e,this.dispatchEvent(new CustomEvent("config-changed",{detail:{config:e},bubbles:!0,composed:!0}))}_setGlobal(e,t){this._emit({...this._config,entities:{...this._config.entities,[e]:t}})}_setRoot(e,t){this._emit({...this._config,[e]:t})}_setPerson(e,t){const i=[...this._config.persons??[]];i[e]={...i[e],...t},this._emit({...this._config,persons:i})}_addPerson(){this._emit({...this._config,persons:[...this._config.persons??[],{entity:""}]})}_removePerson(e){const t=[...this._config.persons??[]];t.splice(e,1),this._emit({...this._config,persons:t})}_sensorPicker(e,t,i,s=["sensor"]){return customElements.get("ha-entity-picker")?I`<ha-entity-picker
        .hass=${this.hass}
        .label=${e}
        .value=${t??""}
        .includeDomains=${s}
        allow-custom-entity
        @value-changed=${e=>i(e.detail.value)}
      ></ha-entity-picker>`:I`<label class="row"><span>${e}</span><input .value=${t??""} @input=${e=>i(e.target.value)} /></label>`}render(){if(!this._config||!this.hass)return I``;const e=this._config.entities;return I`
      <div class="form">
        <label class="row"><span>Titel</span><input .value=${this._config.title??""} @input=${e=>this._setRoot("title",e.target.value)} /></label>

        <h4>Globale Sensoren</h4>
        ${this._sensorPicker("Offene Aufgaben (Pflicht)",e.open_tasks,e=>this._setGlobal("open_tasks",e))}
        ${this._sensorPicker("Fällige Aufgaben",e.due_tasks,e=>this._setGlobal("due_tasks",e))}
        ${this._sensorPicker("Überfällige Aufgaben",e.overdue_tasks,e=>this._setGlobal("overdue_tasks",e))}
        ${this._sensorPicker("Heute erledigt",e.completed_today,e=>this._setGlobal("completed_today",e))}
        ${this._sensorPicker("Diese Woche erledigt",e.completed_this_week,e=>this._setGlobal("completed_this_week",e))}
        ${this._sensorPicker("Aktive Ketten",e.active_chains,e=>this._setGlobal("active_chains",e))}

        <h4>Personen</h4>
        ${(this._config.persons??[]).map((e,t)=>I`
            <div class="person">
              <div class="person-head">
                ${this._sensorPicker("Person",e.entity,e=>this._setPerson(t,{entity:e}),["person"])}
                <button class="del" @click=${()=>this._removePerson(t)} title="Entfernen">✕</button>
              </div>
              ${this._sensorPicker("Offen",e.open_tasks,e=>this._setPerson(t,{open_tasks:e}))}
              ${this._sensorPicker("Fällig",e.due_tasks,e=>this._setPerson(t,{due_tasks:e}))}
              ${this._sensorPicker("Heute erledigt",e.completed_today,e=>this._setPerson(t,{completed_today:e}))}
              ${this._sensorPicker("Verbleibend heute",e.remaining_today,e=>this._setPerson(t,{remaining_today:e}))}
              ${this._sensorPicker("Hat fällige Aufgaben",e.has_due_tasks,e=>this._setPerson(t,{has_due_tasks:e}),["binary_sensor"])}
              ${this._sensorPicker("Kette aktiv",e.chain_active,e=>this._setPerson(t,{chain_active:e}),["binary_sensor"])}
            </div>`)}
        <button class="add" @click=${this._addPerson}>+ Person hinzufügen</button>

        <h4>Optionen</h4>
        <label class="check"><input type="checkbox" .checked=${!1!==this._config.show_create} @change=${e=>this._setRoot("show_create",e.target.checked)} />Erstellen-Dialog anzeigen</label>
        <label class="check"><input type="checkbox" .checked=${!1!==this._config.show_history} @change=${e=>this._setRoot("show_history",e.target.checked)} />Verlauf-Tab anzeigen</label>
        ${this._sensorPicker("Standard-Person",this._config.default_person,e=>this._setRoot("default_person",e),["person"])}
      </div>
    `}};fe.styles=n`
    .form { display: flex; flex-direction: column; gap: 10px; padding: 4px; }
    h4 { margin: 8px 0 0; font-size: 13px; color: var(--secondary-text-color); }
    .row { display: flex; flex-direction: column; gap: 4px; font-size: 12px; color: var(--secondary-text-color); }
    .row input { font: inherit; padding: 8px; border: 1px solid var(--divider-color); border-radius: 6px; background: var(--primary-background-color); color: var(--primary-text-color); }
    .person { border: 1px solid var(--divider-color); border-radius: 8px; padding: 10px; display: flex; flex-direction: column; gap: 8px; }
    .person-head { display: flex; gap: 8px; align-items: flex-end; }
    .person-head ha-entity-picker, .person-head .row { flex: 1; }
    .del { border: none; background: transparent; color: var(--error-color); cursor: pointer; font-size: 14px; padding: 6px; }
    .add { align-self: flex-start; border: 1px dashed var(--divider-color); background: transparent; color: var(--primary-color); border-radius: 6px; padding: 8px 12px; cursor: pointer; font: inherit; }
    .check { display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--primary-text-color); }
  `,e([pe({attribute:!1})],fe.prototype,"hass",void 0),e([ue()],fe.prototype,"_config",void 0),fe=e([ce("choreflow-card-editor")],fe);let ve=class extends ae{constructor(){super(...arguments),this._tab="tasks",this._personFilter="all",this._roomFilter="all",this._categoryFilter="all",this._groupByRoom=!1,this._dialogOpen=!1,this._personPickerOpen=!1,this._pendingAction=null,this._rowState={},this._rowError={},this._tasks=null,this._tasksLoading=!1,this._showTaskRefresh=!1,this._tasksError=null,this._taskRequestGeneration=0,this._taskConfigResetPending=!1,this._editForm=null,this._editSaving=!1,this._editError=null,this._history=[],this._historyTotal=0,this._historyLoading=!1,this._historyOffset=0}static getConfigElement(){return document.createElement("choreflow-card-editor")}static getStubConfig(){return{title:"Haushalt",entities:{open_tasks:"sensor.choreflow_open_tasks",due_tasks:"sensor.choreflow_due_tasks",overdue_tasks:"sensor.choreflow_overdue_tasks",completed_today:"sensor.choreflow_completed_today",completed_this_week:"sensor.choreflow_completed_this_week",active_chains:"sensor.choreflow_active_chains"},persons:[],show_create:!0,show_history:!0}}setConfig(e){if(!e||!e.entities||!e.entities.open_tasks)throw new Error("choreflow-card: 'entities.open_tasks' ist erforderlich (z. B. sensor.choreflow_open_tasks).");const t=this._config,i={show_create:!0,show_history:!0,...e,persons:e.persons??[]},s=i.default_person??"all",o=i.default_room??"all",r=!t||t.entities.open_tasks!==i.entities.open_tasks,n=!t||(t.default_person??"all")!==s,a=!t||(t.default_room??"all")!==o;this._config=i;let l=n;n?this._personFilter=s:"all"===this._personFilter||this._personFilter===s||i.persons.some(e=>e.entity===this._personFilter)||(this._personFilter=s,l=!0),a&&(this._roomFilter=o),t||(this._categoryFilter="all"),(r||l)&&(this._tasks=null,this._tasksError=null,this._taskRequestGeneration+=1,this._taskConfigResetPending=!0)}getCardSize(){return 6}updated(e){const t=e.get("hass"),i=e.get("_config"),s=i?.entities.open_tasks??this._config?.entities.open_tasks,o=this._taskConfigResetPending;this._taskConfigResetPending=!1;const r=e.has("hass")&&(s?t?.states[s]:void 0)!==this._openSensor;this.hass&&this._config&&(o||r)&&this._loadTasks(o||null===this._tasks),"history"===this._tab&&this._config?.show_history&&0===this._history.length&&!this._historyLoading&&0===this._historyOffset&&this._loadHistory(!0)}get _openSensor(){const e=this._config?.entities.open_tasks;return e?this.hass?.states[e]:void 0}_openTasks(){const e=this._openSensor?.attributes?.open_tasks;return Array.isArray(e)?e:[]}_baseTasks(){return null!==this._tasks?this._tasks:"all"===this._personFilter?this._openTasks():[]}_truncatedPreview(){if(null!==this._tasks||"all"!==this._personFilter)return null;const e=this._openSensor?.attributes,t=this._openTasks().length,i=Number(e?.total),s=Number.isFinite(i)?i:null;return!0===e?.truncated||"true"===e?.truncated||null!==s&&s>t?{shown:t,total:s}:null}async _setPersonFilter(e){e===this._personFilter&&null!==this._tasks||(this._personFilter=e,this._roomFilter="all",this._categoryFilter="all",this._tasks=null,this._tasksError=null,await this._loadTasks(!0))}_retryTasks(){this._loadTasks(null===this._tasks)}async _loadTasks(e){const t=++this._taskRequestGeneration,i=e?null:this._tasks;e&&(this._tasks=null),this._tasksLoading=!0,this._showTaskRefresh=!1,void 0!==this._taskRefreshTimer&&(window.clearTimeout(this._taskRefreshTimer),this._taskRefreshTimer=void 0),e?this._tasksError=null:this._taskRefreshTimer=window.setTimeout(()=>{t===this._taskRequestGeneration&&this._tasksLoading&&(this._showTaskRefresh=!0)},300);const s="all"===this._personFilter?void 0:this._personFilter,o=[];let r=0;try{for(;;){const e={status:"open",person_scope:"visible",limit:100,offset:r};s&&(e.person_entity=s);const t=await this.hass.connection.sendMessagePromise({type:"call_service",domain:"choreflow",service:"get_tasks",service_data:e,return_response:!0}),i=this._validateTaskPage(t?.response);if(o.push(...i.items),!i.has_more)break;if(0===i.received)throw new Error("get_tasks returned an empty page with has_more=true");r+=i.received}if(t!==this._taskRequestGeneration)return;this._tasks=o,this._tasksError=null}catch(e){if(t!==this._taskRequestGeneration)return;console.error("[choreflow] get_tasks",e),this._tasks=i,this._tasksError="Aufgaben konnten nicht geladen werden."}finally{t===this._taskRequestGeneration&&(void 0!==this._taskRefreshTimer&&(window.clearTimeout(this._taskRefreshTimer),this._taskRefreshTimer=void 0),this._tasksLoading=!1,this._showTaskRefresh=!1)}}_validateTaskPage(e){if(!e||"object"!=typeof e)throw new Error("Invalid get_tasks response");const t=e;if(!Array.isArray(t.items)||"boolean"!=typeof t.has_more)throw new Error("Invalid get_tasks page");const i=t.items.filter(e=>this._isTask(e)),s=t.items.length-i.length;return s>0&&console.warn(`[choreflow] get_tasks dropped ${s} invalid task item(s)`),{items:i,has_more:t.has_more,received:t.items.length}}_isTask(e){if(!e||"object"!=typeof e)return!1;const t=e;return!("string"!=typeof t.task_id||"string"!=typeof t.title||"string"!=typeof t.room||"string"!=typeof t.category||"low"!==t.importance&&"normal"!==t.importance&&"high"!==t.importance||null!=t.estimated_duration_minutes&&"number"!=typeof t.estimated_duration_minutes||null!=t.due_date&&"string"!=typeof t.due_date||null!=t.snooze_until&&"string"!=typeof t.snooze_until)}_num(e){if(!e)return null;const t=this.hass?.states[e];if(!t||"unknown"===t.state||"unavailable"===t.state)return null;const i=Number(t.state);return Number.isFinite(i)?i:null}_personName(e){const t=this.hass?.states[e.entity];return t?.attributes?.friendly_name||e.entity.split(".").pop()||e.entity}_dueInfo(e){if(!e)return{label:"Kein Termin",overdueDays:0,isOverdue:!1,isToday:!1,rank:100};const t=new Date;t.setHours(0,0,0,0);const i=new Date(e+"T00:00:00"),s=Math.round((i.getTime()-t.getTime())/864e5);if(s<0){const e=-s;return{label:1===e?"Gestern":`vor ${e} Tagen`,overdueDays:e,isOverdue:!0,isToday:!1,rank:1e3+e}}return 0===s?{label:"Heute",overdueDays:0,isOverdue:!1,isToday:!0,rank:600}:1===s?{label:"Morgen",overdueDays:0,isOverdue:!1,isToday:!1,rank:300}:{label:i.toLocaleDateString("de-DE",{weekday:"short",day:"2-digit",month:"2-digit"}),overdueDays:0,isOverdue:!1,isToday:!1,rank:200}}_relTime(e){const t=new Date(e),i=new Date,s=t.toDateString()===i.toDateString(),o=new Date(i);o.setDate(i.getDate()-1);const r=t.toLocaleTimeString("de-DE",{hour:"2-digit",minute:"2-digit"});return s?`Heute ${r}`:t.toDateString()===o.toDateString()?`Gestern ${r}`:t.toLocaleDateString("de-DE",{weekday:"short",day:"2-digit",month:"2-digit"})}_defaultPerson(){return this._config.default_person??("all"!==this._personFilter?this._personFilter:void 0)??this._config.persons?.[0]?.entity}_availablePersonsForPicker(){return this._config.persons?.length?this._config.persons.map(e=>({entity:e.entity,name:this._personName(e)})):Object.keys(this.hass.states).filter(e=>e.startsWith("person.")).map(e=>({entity:e,name:this.hass.states[e].attributes?.friendly_name||e.split(".").pop()||e}))}async _completeTask(e){if("pending"===this._rowState[e]||"done"===this._rowState[e])return;const t=this._defaultPerson();if(!t)return this._pendingAction={taskId:e,action:"complete"},void(this._personPickerOpen=!0);await this._executeComplete(e,t)}async _executeComplete(e,t){this._setRow(e,"pending"),this._clearRowError(e);try{await this.hass.callService("choreflow","complete_task",{task_id:e,person_entity:t,source:"dashboard"}),this._setRow(e,"done")}catch(t){this._setRow(e,"idle"),this._setRowError(e,this._friendlyError(t))}}async _snoozeTask(e){if("pending"===this._rowState[e]||"snoozed"===this._rowState[e])return;const t=this._defaultPerson();if(!t)return this._pendingAction={taskId:e,action:"snooze"},void(this._personPickerOpen=!0);await this._executeSnooze(e,t)}async _executeSnooze(e,t){this._setRow(e,"pending"),this._clearRowError(e);try{await this.hass.callService("choreflow","snooze_task",{task_id:e,person_entity:t}),this._setRow(e,"snoozed")}catch(t){this._setRow(e,"idle"),this._setRowError(e,this._friendlyError(t))}}async _reopenTask(e){try{await this.hass.callService("choreflow","reopen_task",{task_id:e}),await this._loadHistory(!0)}catch(e){console.error("[choreflow] reopen_task",e)}}async _openEdit(e){const t=await this.hass.connection.sendMessagePromise({type:"call_service",domain:"choreflow",service:"get_task",service_data:{task_id:e},return_response:!0}),i=t?.response;i&&(this._editError=null,this._editForm={task_id:e,task_rule_id:i.task_rule_id??null,title:i.title??"",description:i.description??"",room:i.room??"",category:i.category??"",importance:i.importance??"normal",due_date:i.due_date??"",estimated_duration_minutes:null!=i.estimated_duration_minutes?String(i.estimated_duration_minutes):"",recurrence_type:i.recurrence_type??"once",recurrence_interval:null!=i.recurrence_interval?String(i.recurrence_interval):"1",recurrence_weekdays:i.recurrence_weekdays??[]})}_closeEdit(){this._editForm=null,this._editSaving=!1,this._editError=null}_setEditField(e,t){this._editForm&&(this._editForm={...this._editForm,[e]:t},this._editError=null)}_toggleEditWeekday(e){if(!this._editForm)return;const t=this._editForm.recurrence_weekdays,i=t.includes(e)?t.filter(t=>t!==e):[...t,e];this._editForm={...this._editForm,recurrence_weekdays:i},this._editError=null}async _saveEdit(){if(!this._editForm||this._editSaving)return;const e=this._editForm,t=e.estimated_duration_minutes.trim(),i=t?Number(t):null;if(null!==i&&(!Number.isInteger(i)||i<1||i>1440))return void(this._editError="Die Dauer muss eine ganze Zahl zwischen 1 und 1440 Minuten sein.");this._editSaving=!0,this._editError=null;const s={task_id:e.task_id,title:e.title,description:e.description.trim()||null,room:e.room||void 0,category:e.category||void 0,importance:e.importance,due_date:e.due_date||null,estimated_duration_minutes:i};e.task_rule_id&&(s.recurrence_type=e.recurrence_type,"every_n_days"===e.recurrence_type?s.recurrence_interval=Number(e.recurrence_interval)||1:"weekdays"===e.recurrence_type&&(s.recurrence_weekdays=e.recurrence_weekdays));try{await this.hass.callService("choreflow","update_task",s),this._closeEdit()}catch(e){console.error("[choreflow] update_task",e),this._editError=this._friendlyError(e),this._editSaving=!1}}async _createTask(e){const t=await this.hass.connection.sendMessagePromise({type:"call_service",domain:"choreflow",service:"create_task",service_data:e,return_response:!0});return t?.response??{}}async _loadHistory(e=!1){if(!this._config.show_history)return;this._historyLoading=!0;const t=e?0:this._historyOffset;try{const i=await this.hass.connection.sendMessagePromise({type:"call_service",domain:"choreflow",service:"get_history",service_data:{limit:10,offset:t},return_response:!0}),s=i?.response;s&&(this._history=e?s.items:[...this._history,...s.items],this._historyTotal=s.total,this._historyOffset=t+s.items.length)}catch(e){console.error("[choreflow] get_history",e)}finally{this._historyLoading=!1}}_friendlyError(e){const t=e?.message??"";return/visib|sicht/i.test(t)?"Aufgabe ist dir nicht sichtbar.":/assign|zuweis/i.test(t)?"Aufgabe ist dir nicht zugewiesen.":/not open|nicht offen|unknown|unbekannt/i.test(t)?"Aufgabe ist nicht mehr offen.":/person/i.test(t)?"Person ist nicht aktiviert.":"Aktion fehlgeschlagen."}_setRow(e,t){this._rowState={...this._rowState,[e]:t}}_setRowError(e,t){this._rowError={...this._rowError,[e]:t},window.setTimeout(()=>this._clearRowError(e),5e3)}_clearRowError(e){if(!this._rowError[e])return;const t={...this._rowError};delete t[e],this._rowError=t}_localDate(e=new Date){return`${e.getFullYear()}-${String(e.getMonth()+1).padStart(2,"0")}-${String(e.getDate()).padStart(2,"0")}`}_isSnoozed(e){const t=this._localDate();return"snoozed"===this._rowState[e.task_id]||!!e.snooze_until&&e.snooze_until>t}_visibleTasks(){let e=this._baseTasks().filter(e=>"done"!==this._rowState[e.task_id]);return"all"!==this._roomFilter&&(e=e.filter(e=>e.room===this._roomFilter)),"all"!==this._categoryFilter&&(e=e.filter(e=>e.category===this._categoryFilter)),e.slice().sort((e,t)=>{const i=this._isSnoozed(e);return i!==this._isSnoozed(t)?i?1:-1:this._dueInfo(t.due_date).rank+ye(t.importance)-(this._dueInfo(e.due_date).rank+ye(e.importance))})}_rooms(){return[...new Set(this._baseTasks().map(e=>e.room).filter(Boolean))]}_categories(){return[...new Set(this._baseTasks().map(e=>e.category).filter(Boolean))]}render(){if(!this._config||!this.hass)return I``;if(!this._openSensor)return I`<ha-card>
        <div class="error">
          <ha-icon icon="mdi:alert"></ha-icon>
          <div>
            <div class="error-title">ChoreFlow nicht verfügbar</div>
            <div class="error-body">
              Der Pflicht-Sensor <code>${this._config.entities.open_tasks}</code> wurde nicht gefunden.
              Prüfe die Card-Konfiguration und die ChoreFlow-Integration.
            </div>
          </div>
        </div>
      </ha-card>`;const e=this._num(this._config.entities.open_tasks)??this._openTasks().length,t=this._num(this._config.entities.due_tasks),i=this._num(this._config.entities.overdue_tasks),s=this._num(this._config.entities.completed_today);return I`
      <ha-card>
        <div class="head">
          <div class="title">
            <span class="title-text">${this._config.title??"ChoreFlow"}</span>
            <span class="sub">${e} offen</span>
          </div>
          <div class="head-actions">
            ${this._config.show_history?I`<div class="seg" role="tablist">
                  <button role="tab" class=${me({on:"tasks"===this._tab})} @click=${()=>this._tab="tasks"}>Aufgaben</button>
                  <button role="tab" class=${me({on:"history"===this._tab})} @click=${()=>this._tab="history"}>Verlauf</button>
                </div>`:W}
            ${this._config.show_create?I`<button class="icon-btn primary" aria-label="Aufgabe erstellen" title="Aufgabe erstellen" @click=${()=>this._dialogOpen=!0}>
                  <ha-icon icon="mdi:plus"></ha-icon>
                </button>`:W}
          </div>
        </div>

        <div class="stats">
          ${this._stat(e,"Offen")} ${this._stat(t,"Fällig")}
          ${this._stat(i,"Überfällig",i&&i>0?"error":"")}
          ${this._stat(s,"Heute erledigt")}
        </div>

        ${"tasks"===this._tab?this._renderTasks():this._renderHistory()}
      </ha-card>

      ${this._dialogOpen?this._renderDialog():W}
      ${this._personPickerOpen?this._renderPersonPicker():W}
      ${this._editForm?this._renderEditDialog():W}
    `}_stat(e,t,i=""){return I`<div class="stat">
      <div class="stat-num ${i}">${e??"—"}</div>
      <div class="stat-label">${t}</div>
    </div>`}_renderTasks(){const e=this._visibleTasks(),t=this._rooms(),i=this._categories(),s=this._truncatedPreview();return I`
      <div class="filters">
        <div class="seg">
          <button class=${me({on:"all"===this._personFilter})} @click=${()=>{this._setPersonFilter("all")}}>Alle</button>
          ${(this._config.persons??[]).map(e=>I`<button class=${me({on:this._personFilter===e.entity})} @click=${()=>{this._setPersonFilter(e.entity)}}>${this._personName(e)}</button>`)}
        </div>
        <select aria-label="Raum filtern" .value=${this._roomFilter} @change=${e=>this._roomFilter=e.target.value}>
          <option value="all">Alle Räume</option>
          ${t.map(e=>I`<option value=${e}>${e}</option>`)}
        </select>
        <select aria-label="Kategorie filtern" .value=${this._categoryFilter} @change=${e=>this._categoryFilter=e.target.value}>
          <option value="all">Alle Kategorien</option>
          ${i.map(e=>I`<option value=${e}>${e}</option>`)}
        </select>
        <button class=${me({chiptoggle:!0,on:this._groupByRoom})} @click=${()=>this._groupByRoom=!this._groupByRoom}>
          <ha-icon icon="mdi:view-list"></ha-icon>Nach Raum
        </button>
      </div>

      ${this._tasksLoading&&null===this._tasks?I`<div class="task-status"><span class="spin"><ha-icon icon="mdi:loading"></ha-icon></span>Aufgaben werden geladen …</div>`:this._showTaskRefresh?I`<div class="task-status"><span class="spin"><ha-icon icon="mdi:loading"></ha-icon></span>Aufgaben werden aktualisiert …</div>`:W}
      ${this._tasksError?I`<div class="task-status task-error">
            <ha-icon icon="mdi:alert-outline"></ha-icon>
            <span>${this._tasksError}</span>
            <button type="button" @click=${()=>this._retryTasks()}>Erneut versuchen</button>
          </div>`:W}
      ${s?I`<div class="preview-hint">
            <ha-icon icon="mdi:information-outline"></ha-icon>
            <span>
              ${null!==s.total?`Teilansicht: ${s.shown} von ${s.total} offenen Aufgaben werden aus der Sensor-Vorschau angezeigt.`:"Teilansicht: Die Sensor-Vorschau ist gekürzt; weitere offene Aufgaben sind derzeit nicht geladen."}
            </span>
          </div>`:W}

      ${0===e.length&&null===this._tasks&&(this._tasksLoading||this._tasksError)?W:0===e.length?I`<div class="empty"><ha-icon icon="mdi:check"></ha-icon><p>Für diesen Filter ist nichts offen.</p></div>`:this._groupByRoom?this._groupTasks(e):I`<div class="list">${e.map(e=>this._renderRow(e))}</div>`}
    `}_groupTasks(e){const t=new Map;for(const i of e){const e=i.room||"Ohne Raum";t.has(e)||t.set(e,[]),t.get(e).push(i)}return I`<div class="list">
      ${[...t.entries()].map(([e,t])=>I`
          <div class="group-head"><ha-icon icon="mdi:map-marker"></ha-icon>${e}<span class="group-count">· ${t.length}</span></div>
          ${t.map(e=>this._renderRow(e))}
        `)}
    </div>`}_renderRow(e){const t=this._dueInfo(e.due_date),i=e.due_date?Math.round((new Date(e.due_date+"T00:00:00").getTime()-(new Date).setHours(0,0,0,0))/864e5):null;let s="normal";t.isOverdue?s="overdue":"high"===e.importance?s="high":t.isToday&&(s="today");let o="",r="";t.isOverdue?(o="mdi:alert",r=`Überfällig · ${t.overdueDays} ${1===t.overdueDays?"Tag":"Tage"}`):t.isToday&&"high"===e.importance?(o="mdi:alert-circle",r="Heute fällig · Wichtig"):t.isToday?(o="mdi:clock-outline",r="Heute fällig"):"high"===e.importance&&null!==i&&i<=2&&(o="mdi:chevron-up",r=1===i?"Morgen fällig · Wichtig":"Bald fällig · Wichtig");const n=this._rowState[e.task_id]??"idle",a=this._isSnoozed(e),l=this._rowError[e.task_id],c=!!e.task_id,d=[e.room,e.category];return e.estimated_duration_minutes&&d.push(`${e.estimated_duration_minutes} Min`),I`<div class=${me({row:!0,[s]:!0,settled:"done"===n,"row-snoozed":a})}>
      <div class="row-main">
        <div class="row-top">
          <span class="row-title ${"done"===n?"struck":""}">${e.title}</span>
          <span class="due ${s}">${t.label}</span>
        </div>
        <div class="row-meta">
          ${r?I`<span class="urg ${s}"><ha-icon icon=${o}></ha-icon>${r}</span>`:W}
          <span class="meta-text">${r?"· ":""}${d.join(" · ")}</span>
        </div>
        ${a?I`<div class="snooze-badge"><ha-icon icon="mdi:clock-outline"></ha-icon>Aufgeschoben bis morgen</div>`:W}
        ${l?I`<div class="row-error"><ha-icon icon="mdi:alert"></ha-icon>${l}</div>`:W}
      </div>
      <div class="row-actions">
        ${"pending"===n?I`<span class="spin"><ha-icon icon="mdi:loading"></ha-icon></span>`:"done"===n?I`<span class="settle ok"><ha-icon icon="mdi:check-circle"></ha-icon>Erledigt</span>`:a?I`
              <button class="icon-btn ok" aria-label="Erledigen" title="Erledigen" @click=${()=>this._completeTask(e.task_id)}>
                <ha-icon icon="mdi:check-circle"></ha-icon>
              </button>
            `:c?I`
              <button class="icon-btn" aria-label="Bearbeiten" title="Bearbeiten" @click=${()=>this._openEdit(e.task_id)}>
                <ha-icon icon="mdi:pencil"></ha-icon>
              </button>
              <button class="icon-btn" aria-label="Später erinnern" title="Später erinnern" @click=${()=>this._snoozeTask(e.task_id)}>
                <ha-icon icon="mdi:clock-outline"></ha-icon>
              </button>
              <button class="icon-btn ok" aria-label="Erledigen" title="Erledigen" @click=${()=>this._completeTask(e.task_id)}>
                <ha-icon icon="mdi:check-circle"></ha-icon>
              </button>
            `:W}
      </div>
    </div>`}_renderHistory(){return I`
      <div class="hist-head">Verlauf</div>
      ${0===this._history.length&&this._historyLoading?I`<div class="empty"><p>Lädt…</p></div>`:0===this._history.length?I`<div class="empty"><p>Noch keine Einträge.</p></div>`:I`<div class="list">
            ${this._history.map(e=>{const t=function(e){switch(e){case"task_completed":return{icon:"mdi:check-circle",tone:"ok",label:"Erledigt"};case"task_completed_from_todo":return{icon:"mdi:clipboard-check",tone:"ok",label:"Erledigt (To-do)"};case"task_reopened":return{icon:"mdi:undo",tone:"warn",label:"Korrigiert"};case"task_snoozed":return{icon:"mdi:clock-outline",tone:"warn",label:"Später erinnert"};case"task_created":return{icon:"mdi:plus-circle-outline",tone:"muted",label:"Erstellt"};case"task_updated":return{icon:"mdi:pencil",tone:"muted",label:"Geändert"};case"task_deleted":return{icon:"mdi:delete-outline",tone:"muted",label:"Gelöscht"};case"task_notified":return{icon:"mdi:bell-outline",tone:"muted",label:"Benachrichtigt"};case"task_missed_no_presence":return{icon:"mdi:account-off-outline",tone:"err",label:"Verpasst (abwesend)"};case"task_expired":return{icon:"mdi:close-circle-outline",tone:"err",label:"Abgelaufen"};case"task_synced_from_todo":return{icon:"mdi:sync",tone:"muted",label:"Aus To-do"};case"calendar_task_created":return{icon:"mdi:calendar-plus",tone:"muted",label:"Kalender erstellt"};case"calendar_task_removed":return{icon:"mdi:calendar-remove",tone:"muted",label:"Kalender entfernt"};default:return{icon:"mdi:information-outline",tone:"muted",label:e}}}(e.event_type),i=("task_completed"===e.event_type||"task_completed_from_todo"===e.event_type)&&!!e.task_id,s=[t.label,e.room,e.person_entity?be(this.hass,e.person_entity):null].filter(Boolean);return I`<div class="hist">
                <ha-icon class=${t.tone} icon=${t.icon}></ha-icon>
                <div class="hist-main">
                  <div class="hist-top">
                    <span class="hist-title">${e.title??"—"}</span>
                    <span class="hist-time">${this._relTime(e.timestamp)}</span>
                  </div>
                  <div class="hist-meta">${s.join(" · ")}</div>
                </div>
                ${i?I`<button class="icon-btn" aria-label="Korrigieren" title="Erledigung rückgängig machen" @click=${()=>this._reopenTask(e.task_id)}>
                      <ha-icon icon="mdi:undo"></ha-icon>
                    </button>`:W}
              </div>`})}
          </div>`}
      ${this._historyOffset<this._historyTotal?I`<button class="loadmore" ?disabled=${this._historyLoading} @click=${()=>this._loadHistory(!1)}>
            ${this._historyLoading?"Lädt…":"Mehr laden"}
          </button>`:W}
    `}_renderPersonPicker(){const e=this._availablePersonsForPicker(),t=()=>{this._personPickerOpen=!1,this._pendingAction=null},i=async e=>{this._personPickerOpen=!1;const t=this._pendingAction;this._pendingAction=null,t&&("complete"===t.action?await this._executeComplete(t.taskId,e):await this._executeSnooze(t.taskId,e))};return I`<div class="overlay" @click=${t}>
      <div class="dialog" style="max-width:320px" @click=${e=>e.stopPropagation()}>
        <div class="dlg-head">
          <span>Wer bist du?</span>
          <button type="button" class="icon-btn" aria-label="Schließen" @click=${t}><ha-icon icon="mdi:close"></ha-icon></button>
        </div>
        <div class="dlg-body">
          ${e.length?e.map(e=>I`<button class="person-pick-btn" @click=${()=>i(e.entity)}>${e.name}</button>`):I`<p style="margin:0;font-size:13px;color:var(--secondary-text-color)">Keine Personen gefunden. Bitte <code>persons</code> oder <code>default_person</code> in der Kartenkonfiguration setzen.</p>`}
        </div>
      </div>
    </div>`}_renderEditDialog(){const e=this._editForm,t=!!e.task_rule_id;return I`<div class="overlay" @click=${()=>this._closeEdit()}>
      <div class="dialog edit-dialog" @click=${e=>e.stopPropagation()}>
        <div class="dlg-head">
          <span>Aufgabe bearbeiten</span>
          <button type="button" class="icon-btn" aria-label="Schließen" @click=${()=>this._closeEdit()}>
            <ha-icon icon="mdi:close"></ha-icon>
          </button>
        </div>
        <div class="dlg-body edit-body">
          ${this._editError?I`<div class="edit-error" role="alert"><ha-icon icon="mdi:alert-outline"></ha-icon>${this._editError}</div>`:W}
          <label class="edit-label">Titel
            <input class="edit-input" type="text" .value=${e.title}
              @input=${e=>this._setEditField("title",e.target.value)} />
          </label>
          <label class="edit-label">Beschreibung
            <textarea class="edit-input edit-textarea" rows="2"
              @input=${e=>this._setEditField("description",e.target.value)}
            >${e.description}</textarea>
          </label>
          <div class="edit-row2">
            <label class="edit-label">Raum
              <input class="edit-input" type="text" .value=${e.room}
                @input=${e=>this._setEditField("room",e.target.value)} />
            </label>
            <label class="edit-label">Kategorie
              <input class="edit-input" type="text" .value=${e.category}
                @input=${e=>this._setEditField("category",e.target.value)} />
            </label>
          </div>
          <div class="edit-row2">
            <label class="edit-label">Wichtigkeit
              <select class="edit-input" .value=${e.importance}
                @change=${e=>this._setEditField("importance",e.target.value)}>
                <option value="high" ?selected=${"high"===e.importance}>Hoch</option>
                <option value="normal" ?selected=${"normal"===e.importance}>Normal</option>
                <option value="low" ?selected=${"low"===e.importance}>Niedrig</option>
              </select>
            </label>
            <label class="edit-label">Dauer (Min)
              <input class="edit-input" type="number" min="1" max="1440" .value=${e.estimated_duration_minutes}
                @input=${e=>this._setEditField("estimated_duration_minutes",e.target.value)} />
            </label>
          </div>
          <label class="edit-label">Fälligkeitsdatum
            <input class="edit-input" type="date" .value=${e.due_date}
              @change=${e=>this._setEditField("due_date",e.target.value)} />
          </label>
          ${t?I`
            <div class="edit-section-head">Wiederholung</div>
            <div class="edit-recurrence-btns">
              ${["once","every_n_days","weekdays"].map(t=>I`
                <button class=${me({"recurrence-btn":!0,active:e.recurrence_type===t})}
                  type="button" @click=${()=>this._setEditField("recurrence_type",t)}>
                  ${{once:"Einmalig",every_n_days:"Alle N Tage",weekdays:"Wochentage"}[t]}
                </button>`)}
            </div>
            ${"every_n_days"===e.recurrence_type?I`
              <label class="edit-label">Intervall (Tage)
                <input class="edit-input" type="number" min="1" max="365" .value=${e.recurrence_interval}
                  @input=${e=>this._setEditField("recurrence_interval",e.target.value)} />
              </label>`:W}
            ${"weekdays"===e.recurrence_type?I`
              <div class="weekday-picker">
                ${["Mo","Di","Mi","Do","Fr","Sa","So"].map((t,i)=>I`
                  <button type="button"
                    class=${me({"wd-btn":!0,active:e.recurrence_weekdays.includes(i)})}
                    @click=${()=>this._toggleEditWeekday(i)}>${t}</button>`)}
              </div>`:W}
          `:W}
        </div>
        <div class="dlg-footer">
          <button class="dlg-btn secondary" type="button" @click=${()=>this._closeEdit()}>Abbrechen</button>
          <button class="dlg-btn primary" type="button" ?disabled=${this._editSaving} @click=${()=>this._saveEdit()}>
            ${this._editSaving?I`<ha-icon icon="mdi:loading" style="animation:spin .8s linear infinite"></ha-icon>`:W}
            Speichern
          </button>
        </div>
      </div>
    </div>`}_renderDialog(){const e=this._rooms(),t=this._categories(),i=this._config.persons??[],s=()=>this._dialogOpen=!1;return I`<div class="overlay" @click=${s}>
      <form class="dialog" @click=${e=>e.stopPropagation()} @submit=${async e=>{e.preventDefault();const t=e.target.closest("form"),i=new FormData(t),o=String(i.get("title")??"").trim();if(!o)return void t.querySelector("[name=title]")?.focus();const r=String(i.get("visibility_mode")||"all_enabled_persons"),n=String(i.get("assignment_mode")||"random"),a=String(i.get("calendar_export_entity_id")||"").trim()||void 0,l={title:o,description:String(i.get("description")||"")||void 0,room:String(i.get("room")||"")||void 0,category:String(i.get("category")||"")||void 0,importance:String(i.get("importance")||"normal"),estimated_duration_minutes:i.get("duration")?Number(i.get("duration")):void 0,due_date:String(i.get("due_date")||"")||void 0,visibility_mode:r,visibility_persons:"selected_persons"===r?i.getAll("visibility_persons").map(String):void 0,assignment_mode:n,assignment_person:"assigned"===n&&String(i.get("assignment_person")||"")||void 0,calendar_export_entity_id:a};try{await this._createTask(l),s()}catch(e){console.error("[choreflow] create_task",e)}}}>
        <div class="dlg-head">
          <span>Neue Aufgabe</span>
          <button type="button" class="icon-btn" aria-label="Schließen" @click=${s}><ha-icon icon="mdi:close"></ha-icon></button>
        </div>
        <div class="dlg-body">
          <label>Titel<input name="title" placeholder="z. B. Bad putzen" autofocus /></label>
          <div class="two">
            <label>Raum<input name="room" list="cf-rooms" placeholder="Küche" /></label>
            <label>Kategorie<input name="category" list="cf-cats" placeholder="Reinigung" /></label>
          </div>
          <datalist id="cf-rooms">${e.map(e=>I`<option value=${e}></option>`)}</datalist>
          <datalist id="cf-cats">${t.map(e=>I`<option value=${e}></option>`)}</datalist>
          <fieldset class="radios">
            <legend>Wichtigkeit</legend>
            ${["low","normal","high"].map((e,t)=>I`<label class="radio"><input type="radio" name="importance" value=${e} ?checked=${1===t} />${{low:"Niedrig",normal:"Normal",high:"Hoch"}[e]}</label>`)}
          </fieldset>
          <div class="two">
            <label>Dauer (Min)<input name="duration" type="number" min="0" placeholder="15" /></label>
            <label>Fällig am<input name="due_date" type="date" /></label>
          </div>
          <details>
            <summary>Sichtbarkeit &amp; Zuweisung</summary>
            <fieldset class="radios">
              <legend>Sichtbar für</legend>
              <label class="radio"><input type="radio" name="visibility_mode" value="all_enabled_persons" checked />Alle Personen</label>
              <label class="radio"><input type="radio" name="visibility_mode" value="selected_persons" />Ausgewählte</label>
            </fieldset>
            ${i.length?I`<div class="chips">
                  ${i.map(e=>I`<label class="chip-check"><input type="checkbox" name="visibility_persons" value=${e.entity} />${this._personName(e)}</label>`)}
                </div>`:W}
            <fieldset class="radios">
              <legend>Zuweisung</legend>
              <label class="radio"><input type="radio" name="assignment_mode" value="random" checked />Zufällig</label>
              <label class="radio"><input type="radio" name="assignment_mode" value="assigned" />Feste Person</label>
            </fieldset>
            <label>Person<select name="assignment_person">
              <option value="">Person wählen…</option>
              ${i.map(e=>I`<option value=${e.entity}>${this._personName(e)}</option>`)}
            </select></label>
          </details>
          <details>
            <summary>Kalender-Export</summary>
            <label style="margin-top:8px">
              Kalender-Entität (optional)
              <input
                name="calendar_export_entity_id"
                placeholder="calendar.outlook_kalender"
                autocomplete="off"
              />
            </label>
            <p style="font-size:11px;color:var(--secondary-text-color);margin:4px 0 0">
              Falls angegeben, wird der Fälligkeitstermin als Termin im gewählten Kalender angelegt.
            </p>
          </details>
        </div>
        <div class="dlg-foot">
          <button type="button" class="btn ghost" @click=${s}>Abbrechen</button>
          <button type="submit" class="btn primary">Erstellen</button>
        </div>
      </form>
    </div>`}};function ye(e){return"high"===e?40:"low"===e?-20:0}function be(e,t){const i=e.states[t];return i?.attributes?.friendly_name||t.split(".").pop()||t}ve.styles=n`
    :host { display: block; }
    ha-card { overflow: hidden; }
    ha-icon { --mdc-icon-size: 20px; display: inline-flex; }

    .head { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 14px 16px 12px; }
    .title { display: flex; align-items: baseline; gap: 9px; min-width: 0; }
    .title-text { font-size: 16px; font-weight: 500; }
    .sub { font-size: 12px; color: var(--secondary-text-color); white-space: nowrap; }
    .head-actions { display: flex; align-items: center; gap: 6px; }

    .seg { display: flex; gap: 2px; background: var(--primary-background-color); border-radius: 6px; padding: 2px; }
    .seg button { border: none; border-radius: 5px; padding: 5px 11px; font: inherit; font-size: 12px; font-weight: 500; cursor: pointer; background: transparent; color: var(--secondary-text-color); }
    .seg button.on { background: var(--card-background-color); color: var(--primary-text-color); box-shadow: 0 1px 2px rgba(0,0,0,.15); }

    .icon-btn { display: inline-flex; align-items: center; justify-content: center; width: 32px; height: 32px; border: none; border-radius: 6px; background: transparent; color: var(--secondary-text-color); cursor: pointer; }
    .icon-btn.ok { color: var(--success-color, var(--primary-color)); }
    .icon-btn.primary { width: 34px; height: 34px; background: var(--primary-color); color: var(--text-primary-color, #fff); }

    .stats { display: grid; grid-template-columns: repeat(4, 1fr); border-top: 1px solid var(--divider-color); border-bottom: 1px solid var(--divider-color); }
    .stat { padding: 11px 14px; }
    .stat + .stat { border-left: 1px solid var(--divider-color); }
    .stat-num { font-size: 22px; font-weight: 500; line-height: 1.1; }
    .stat-num.error { color: var(--error-color); }
    .stat-label { font-size: 10.5px; font-weight: 500; letter-spacing: .05em; text-transform: uppercase; color: var(--secondary-text-color); margin-top: 3px; }



    .filters { padding: 10px 16px; border-bottom: 1px solid var(--divider-color); display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
    .filters select { font: inherit; font-size: 12px; color: var(--primary-text-color); background: var(--primary-background-color); border: 1px solid var(--divider-color); border-radius: 6px; padding: 6px 8px; cursor: pointer; }
    .task-status { display: flex; align-items: center; gap: 8px; padding: 10px 16px; font-size: 12px; color: var(--secondary-text-color); border-bottom: 1px solid var(--divider-color); }
    .task-status.task-error { color: var(--error-color); }
    .task-status button { margin-left: auto; border: 1px solid var(--divider-color); border-radius: 6px; padding: 5px 8px; color: var(--primary-text-color); background: transparent; font: inherit; cursor: pointer; }
    .preview-hint { display: flex; align-items: center; gap: 7px; padding: 9px 16px; font-size: 12px; line-height: 1.4; color: var(--secondary-text-color); background: color-mix(in srgb, var(--warning-color, #ff9800) 8%, transparent); border-bottom: 1px solid var(--divider-color); }
    .preview-hint ha-icon { --mdc-icon-size: 17px; color: var(--warning-color, #ff9800); flex: 0 0 auto; }
    .chiptoggle { display: inline-flex; align-items: center; gap: 5px; border: 1px solid var(--divider-color); border-radius: 6px; padding: 6px 9px; font: inherit; font-size: 12px; font-weight: 500; cursor: pointer; background: transparent; color: var(--secondary-text-color); }
    .chiptoggle ha-icon { --mdc-icon-size: 14px; }
    .chiptoggle.on { background: var(--primary-color); color: var(--text-primary-color, #fff); border-color: var(--primary-color); }

    .list { display: flex; flex-direction: column; }
    .group-head { display: flex; align-items: center; gap: 7px; padding: 9px 16px 5px; font-size: 11px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; color: var(--secondary-text-color); background: var(--primary-background-color); }
    .group-head ha-icon { --mdc-icon-size: 13px; }
    .group-count { font-weight: 400; text-transform: none; letter-spacing: 0; }

    .row { position: relative; display: flex; gap: 11px; align-items: flex-start; padding: 13px 16px; border-bottom: 1px solid var(--divider-color); transition: opacity .3s; }
    .row::before { content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 3px; background: var(--divider-color); }
    .row.overdue::before { background: var(--error-color); }
    .row.high::before { background: var(--warning-color); }
    .row.today::before { background: var(--primary-color); }
    .row.settled { opacity: .5; }
    .row.row-snoozed { opacity: .65; }
    .snooze-badge { display: inline-flex; align-items: center; gap: 4px; margin-top: 5px; font-size: 11.5px; color: var(--warning-color); }
    .snooze-badge ha-icon { --mdc-icon-size: 13px; }
    .row-main { flex: 1; min-width: 0; }
    .row-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; }
    .row-title { font-size: 14px; font-weight: 500; line-height: 1.35; }
    .row-title.struck { text-decoration: line-through; }
    .due { flex: none; border: 1px solid var(--divider-color); border-radius: 4px; padding: 1px 6px; font-size: 11px; line-height: 1.5; white-space: nowrap; color: var(--secondary-text-color); }
    .due.overdue { color: var(--error-color); }
    .due.today { color: var(--primary-color); }
    .row-meta { display: flex; align-items: center; gap: 6px; margin-top: 5px; flex-wrap: wrap; }
    .urg { display: inline-flex; align-items: center; gap: 4px; font-size: 12px; font-weight: 500; }
    .urg ha-icon { --mdc-icon-size: 14px; }
    .urg.overdue { color: var(--error-color); }
    .urg.high { color: var(--warning-color); }
    .urg.today { color: var(--primary-color); }
    .meta-text { font-size: 12px; color: var(--secondary-text-color); }
    .row-error { display: flex; align-items: center; gap: 5px; margin-top: 6px; color: var(--error-color); font-size: 11.5px; }
    .row-error ha-icon { --mdc-icon-size: 13px; }
    .row-actions { flex: none; display: flex; align-items: center; gap: 2px; min-height: 32px; }
    .settle { display: inline-flex; align-items: center; gap: 4px; font-size: 12px; padding-right: 6px; }
    .settle.ok { color: var(--success-color, var(--primary-color)); }
    .settle.warn { color: var(--warning-color); }
    .settle ha-icon { --mdc-icon-size: 16px; }
    .spin ha-icon { color: var(--secondary-text-color); animation: spin .8s linear infinite; }
    @keyframes spin { to { transform: rotate(360deg); } }

    .empty { padding: 38px 16px; text-align: center; color: var(--secondary-text-color); }
    .empty ha-icon { --mdc-icon-size: 30px; opacity: .55; }
    .empty p { margin: 10px 0 0; font-size: 13px; }

    .hist-head { padding: 9px 16px; font-size: 11px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; color: var(--secondary-text-color); border-bottom: 1px solid var(--divider-color); }
    .hist { display: flex; gap: 11px; align-items: flex-start; padding: 11px 16px; border-bottom: 1px solid var(--divider-color); }
    .hist ha-icon { flex: none; margin-top: 1px; }
    .hist ha-icon.ok { color: var(--success-color, var(--primary-color)); }
    .hist ha-icon.warn { color: var(--warning-color); }
    .hist ha-icon.err { color: var(--error-color); }
    .hist ha-icon.muted { color: var(--secondary-text-color); }
    .hist-main { flex: 1; min-width: 0; }
    .hist-top { display: flex; justify-content: space-between; gap: 8px; }
    .hist-title { font-size: 13.5px; font-weight: 500; }
    .hist-time { flex: none; font-size: 11.5px; color: var(--secondary-text-color); white-space: nowrap; }
    .hist-meta { font-size: 12px; color: var(--secondary-text-color); margin-top: 3px; }
    .loadmore { width: 100%; border: none; background: transparent; color: var(--primary-color); font: inherit; font-size: 13px; font-weight: 500; cursor: pointer; padding: 13px; }

    .error { display: flex; gap: 10px; padding: 18px; border-left: 3px solid var(--error-color); }
    .error ha-icon { color: var(--error-color); --mdc-icon-size: 22px; }
    .error-title { font-size: 15px; font-weight: 500; }
    .error-body { margin-top: 8px; font-size: 13px; line-height: 1.5; color: var(--secondary-text-color); }
    code { font-family: ui-monospace, monospace; font-size: 12px; background: var(--primary-background-color); padding: 1px 5px; border-radius: 4px; }

    .overlay { position: fixed; inset: 0; background: rgba(0,0,0,.46); display: flex; align-items: flex-start; justify-content: center; padding: 40px 16px; z-index: 9; overflow: auto; }
    .dialog { width: 100%; max-width: 440px; background: var(--card-background-color); color: var(--primary-text-color); border-radius: 8px; box-shadow: 0 12px 40px rgba(0,0,0,.4); overflow: hidden; }
    .dlg-head { display: flex; align-items: center; justify-content: space-between; padding: 15px 16px; border-bottom: 1px solid var(--divider-color); font-size: 15px; font-weight: 500; }
    .dlg-body { padding: 16px; display: flex; flex-direction: column; gap: 13px; max-height: 64vh; overflow: auto; }
    .dlg-body label { display: flex; flex-direction: column; gap: 5px; font-size: 12px; color: var(--secondary-text-color); font-weight: 500; }
    .person-pick-btn { width: 100%; font: inherit; font-size: 14px; font-weight: 500; color: var(--primary-text-color); background: var(--primary-background-color); border: 1px solid var(--divider-color); border-radius: 8px; padding: 12px 16px; cursor: pointer; text-align: left; }
    .person-pick-btn:hover { background: var(--secondary-background-color); }
    .dlg-body input, .dlg-body select { font: inherit; font-size: 14px; color: var(--primary-text-color); background: var(--primary-background-color); border: 1px solid var(--divider-color); border-radius: 6px; padding: 9px 10px; outline: none; }
    .two { display: flex; gap: 10px; }
    .two label { flex: 1; }
    fieldset.radios { border: none; padding: 0; margin: 0; }
    fieldset.radios legend { font-size: 12px; color: var(--secondary-text-color); font-weight: 500; padding: 0; margin-bottom: 6px; }
    .radio, .chip-check { display: inline-flex; align-items: center; gap: 5px; font-size: 13px; color: var(--primary-text-color); margin-right: 12px; }
    .chips { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 8px; }
    details summary { font-size: 13px; font-weight: 500; cursor: pointer; padding: 8px 0; border-top: 1px solid var(--divider-color); }
    .dlg-foot { display: flex; justify-content: flex-end; gap: 8px; padding: 13px 16px; border-top: 1px solid var(--divider-color); }
    .btn { border-radius: 6px; padding: 9px 16px; font: inherit; font-size: 13px; font-weight: 500; cursor: pointer; }
    .btn.ghost { border: 1px solid var(--divider-color); background: transparent; color: var(--primary-text-color); }
    .btn.primary { border: none; background: var(--primary-color); color: var(--text-primary-color, #fff); }

    /* ---- edit dialog ---- */
    .edit-dialog { max-width: 500px; }
    .edit-body { gap: 12px; }
    .edit-label { display: flex; flex-direction: column; gap: 5px; font-size: 12px; color: var(--secondary-text-color); font-weight: 500; }
    .edit-input { font: inherit; font-size: 14px; color: var(--primary-text-color); background: var(--primary-background-color); border: 1px solid var(--divider-color); border-radius: 6px; padding: 8px 10px; outline: none; width: 100%; box-sizing: border-box; }
    .edit-input:focus { border-color: var(--primary-color); }
    .edit-textarea { resize: vertical; min-height: 56px; font-family: inherit; }
    .edit-error { display: flex; align-items: center; gap: 7px; padding: 9px 10px; border-radius: 6px; color: var(--error-color); background: color-mix(in srgb, var(--error-color) 10%, transparent); font-size: 12px; line-height: 1.4; }
    .edit-error ha-icon { --mdc-icon-size: 17px; flex: 0 0 auto; }
    .edit-row2 { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    .edit-section-head { font-size: 12px; font-weight: 600; color: var(--secondary-text-color); text-transform: uppercase; letter-spacing: .05em; padding-top: 4px; border-top: 1px solid var(--divider-color); }
    .edit-recurrence-btns { display: flex; gap: 6px; flex-wrap: wrap; }
    .recurrence-btn { font: inherit; font-size: 13px; padding: 6px 12px; border: 1px solid var(--divider-color); border-radius: 20px; background: transparent; color: var(--secondary-text-color); cursor: pointer; }
    .recurrence-btn.active { border-color: var(--primary-color); background: var(--primary-color); color: var(--text-primary-color, #fff); }
    .weekday-picker { display: flex; gap: 5px; flex-wrap: wrap; }
    .wd-btn { font: inherit; font-size: 13px; font-weight: 500; width: 38px; height: 38px; border: 1px solid var(--divider-color); border-radius: 50%; background: transparent; color: var(--secondary-text-color); cursor: pointer; }
    .wd-btn.active { border-color: var(--primary-color); background: var(--primary-color); color: var(--text-primary-color, #fff); }
    .dlg-footer { display: flex; justify-content: flex-end; gap: 8px; padding: 13px 16px; border-top: 1px solid var(--divider-color); }
    .dlg-btn { border-radius: 6px; padding: 9px 18px; font: inherit; font-size: 13px; font-weight: 500; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; }
    .dlg-btn.secondary { border: 1px solid var(--divider-color); background: transparent; color: var(--primary-text-color); }
    .dlg-btn.primary { border: none; background: var(--primary-color); color: var(--text-primary-color, #fff); }
    .dlg-btn:disabled { opacity: .6; cursor: default; }
    .dlg-btn ha-icon { --mdc-icon-size: 16px; }

    @media (prefers-reduced-motion: reduce) { * { animation-duration: .001ms !important; transition-duration: .001ms !important; } }
  `,e([pe({attribute:!1})],ve.prototype,"hass",void 0),e([ue()],ve.prototype,"_config",void 0),e([ue()],ve.prototype,"_tab",void 0),e([ue()],ve.prototype,"_personFilter",void 0),e([ue()],ve.prototype,"_roomFilter",void 0),e([ue()],ve.prototype,"_categoryFilter",void 0),e([ue()],ve.prototype,"_groupByRoom",void 0),e([ue()],ve.prototype,"_dialogOpen",void 0),e([ue()],ve.prototype,"_personPickerOpen",void 0),e([ue()],ve.prototype,"_pendingAction",void 0),e([ue()],ve.prototype,"_rowState",void 0),e([ue()],ve.prototype,"_rowError",void 0),e([ue()],ve.prototype,"_tasks",void 0),e([ue()],ve.prototype,"_tasksLoading",void 0),e([ue()],ve.prototype,"_showTaskRefresh",void 0),e([ue()],ve.prototype,"_tasksError",void 0),e([ue()],ve.prototype,"_editForm",void 0),e([ue()],ve.prototype,"_editSaving",void 0),e([ue()],ve.prototype,"_editError",void 0),e([ue()],ve.prototype,"_history",void 0),e([ue()],ve.prototype,"_historyTotal",void 0),e([ue()],ve.prototype,"_historyLoading",void 0),e([ue()],ve.prototype,"_historyOffset",void 0),ve=e([ce("choreflow-card")],ve),window.customCards=window.customCards||[],window.customCards.push({type:"choreflow-card",name:"ChoreFlow Card",description:"Ruhige, kompakte Aufgaben-Card für die ChoreFlow-Integration.",preview:!0,documentationURL:"https://github.com/your-org/ha-choreflow-card"});export{ve as ChoreFlowCard};
