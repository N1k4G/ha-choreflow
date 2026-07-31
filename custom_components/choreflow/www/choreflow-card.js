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
function t(t,e,i,s){var o,r=arguments.length,n=r<3?e:null===s?s=Object.getOwnPropertyDescriptor(e,i):s;if("object"==typeof Reflect&&"function"==typeof Reflect.decorate)n=Reflect.decorate(t,e,i,s);else for(var a=t.length-1;a>=0;a--)(o=t[a])&&(n=(r<3?o(n):r>3?o(e,i,n):o(e,i))||n);return r>3&&n&&Object.defineProperty(e,i,n),n}"function"==typeof SuppressedError&&SuppressedError;const e=globalThis,i=e.ShadowRoot&&(void 0===e.ShadyCSS||e.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,s=Symbol(),o=new WeakMap;let r=class{constructor(t,e,i){if(this._$cssResult$=!0,i!==s)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o;const e=this.t;if(i&&void 0===t){const i=void 0!==e&&1===e.length;i&&(t=o.get(e)),void 0===t&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),i&&o.set(e,t))}return t}toString(){return this.cssText}};const n=(t,...e)=>{const i=1===t.length?t[0]:e.reduce((e,i,s)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+t[s+1],t[0]);return new r(i,t,s)},a=i?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const i of t.cssRules)e+=i.cssText;return(t=>new r("string"==typeof t?t:t+"",void 0,s))(e)})(t):t,{is:l,defineProperty:c,getOwnPropertyDescriptor:d,getOwnPropertyNames:p,getOwnPropertySymbols:h,getPrototypeOf:u}=Object,_=globalThis,g=_.trustedTypes,m=g?g.emptyScript:"",f=_.reactiveElementPolyfillSupport,y=(t,e)=>t,v={toAttribute(t,e){switch(e){case Boolean:t=t?m:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let i=t;switch(e){case Boolean:i=null!==t;break;case Number:i=null===t?null:Number(t);break;case Object:case Array:try{i=JSON.parse(t)}catch(t){i=null}}return i}},b=(t,e)=>!l(t,e),x={attribute:!0,type:String,converter:v,reflect:!1,useDefault:!1,hasChanged:b};Symbol.metadata??=Symbol("metadata"),_.litPropertyMetadata??=new WeakMap;let $=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=x){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){const i=Symbol(),s=this.getPropertyDescriptor(t,i,e);void 0!==s&&c(this.prototype,t,s)}}static getPropertyDescriptor(t,e,i){const{get:s,set:o}=d(this.prototype,t)??{get(){return this[e]},set(t){this[e]=t}};return{get:s,set(e){const r=s?.call(this);o?.call(this,e),this.requestUpdate(t,r,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??x}static _$Ei(){if(this.hasOwnProperty(y("elementProperties")))return;const t=u(this);t.finalize(),void 0!==t.l&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(y("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(y("properties"))){const t=this.properties,e=[...p(t),...h(t)];for(const i of e)this.createProperty(i,t[i])}const t=this[Symbol.metadata];if(null!==t){const e=litPropertyMetadata.get(t);if(void 0!==e)for(const[t,i]of e)this.elementProperties.set(t,i)}this._$Eh=new Map;for(const[t,e]of this.elementProperties){const i=this._$Eu(t,e);void 0!==i&&this._$Eh.set(i,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const i=new Set(t.flat(1/0).reverse());for(const t of i)e.unshift(a(t))}else void 0!==t&&e.push(a(t));return e}static _$Eu(t,e){const i=e.attribute;return!1===i?void 0:"string"==typeof i?i:"string"==typeof t?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),void 0!==this.renderRoot&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){const t=new Map,e=this.constructor.elementProperties;for(const i of e.keys())this.hasOwnProperty(i)&&(t.set(i,this[i]),delete this[i]);t.size>0&&(this._$Ep=t)}createRenderRoot(){const t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return((t,s)=>{if(i)t.adoptedStyleSheets=s.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(const i of s){const s=document.createElement("style"),o=e.litNonce;void 0!==o&&s.setAttribute("nonce",o),s.textContent=i.cssText,t.appendChild(s)}})(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,i){this._$AK(t,i)}_$ET(t,e){const i=this.constructor.elementProperties.get(t),s=this.constructor._$Eu(t,i);if(void 0!==s&&!0===i.reflect){const o=(void 0!==i.converter?.toAttribute?i.converter:v).toAttribute(e,i.type);this._$Em=t,null==o?this.removeAttribute(s):this.setAttribute(s,o),this._$Em=null}}_$AK(t,e){const i=this.constructor,s=i._$Eh.get(t);if(void 0!==s&&this._$Em!==s){const t=i.getPropertyOptions(s),o="function"==typeof t.converter?{fromAttribute:t.converter}:void 0!==t.converter?.fromAttribute?t.converter:v;this._$Em=s;const r=o.fromAttribute(e,t.type);this[s]=r??this._$Ej?.get(s)??r,this._$Em=null}}requestUpdate(t,e,i,s=!1,o){if(void 0!==t){const r=this.constructor;if(!1===s&&(o=this[t]),i??=r.getPropertyOptions(t),!((i.hasChanged??b)(o,e)||i.useDefault&&i.reflect&&o===this._$Ej?.get(t)&&!this.hasAttribute(r._$Eu(t,i))))return;this.C(t,e,i)}!1===this.isUpdatePending&&(this._$ES=this._$EP())}C(t,e,{useDefault:i,reflect:s,wrapped:o},r){i&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,r??e??this[t]),!0!==o||void 0!==r)||(this._$AL.has(t)||(this.hasUpdated||i||(e=void 0),this._$AL.set(t,e)),!0===s&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(const[t,e]of this._$Ep)this[t]=e;this._$Ep=void 0}const t=this.constructor.elementProperties;if(t.size>0)for(const[e,i]of t){const{wrapped:t}=i,s=this[e];!0!==t||this._$AL.has(e)||void 0===s||this.C(e,void 0,i,s)}}let t=!1;const e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(t=>t.hostUpdate?.()),this.update(e)):this._$EM()}catch(e){throw t=!1,this._$EM(),e}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(t=>this._$ET(t,this[t])),this._$EM()}updated(t){}firstUpdated(t){}};$.elementStyles=[],$.shadowRootOptions={mode:"open"},$[y("elementProperties")]=new Map,$[y("finalized")]=new Map,f?.({ReactiveElement:$}),(_.reactiveElementVersions??=[]).push("2.1.2");const k=globalThis,w=t=>t,A=k.trustedTypes,E=A?A.createPolicy("lit-html",{createHTML:t=>t}):void 0,S="$lit$",P=`lit$${Math.random().toFixed(9).slice(2)}$`,z="?"+P,T=`<${z}>`,C=document,F=()=>C.createComment(""),O=t=>null===t||"object"!=typeof t&&"function"!=typeof t,R=Array.isArray,D="[ \t\n\f\r]",M=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,H=/-->/g,N=/>/g,U=RegExp(`>|${D}(?:([^\\s"'>=/]+)(${D}*=${D}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),j=/'/g,L=/"/g,B=/^(?:script|style|textarea|title)$/i,I=(t=>(e,...i)=>({_$litType$:t,strings:e,values:i}))(1),K=Symbol.for("lit-noChange"),W=Symbol.for("lit-nothing"),G=new WeakMap,q=C.createTreeWalker(C,129);function V(t,e){if(!R(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==E?E.createHTML(e):e}const Z=(t,e)=>{const i=t.length-1,s=[];let o,r=2===e?"<svg>":3===e?"<math>":"",n=M;for(let e=0;e<i;e++){const i=t[e];let a,l,c=-1,d=0;for(;d<i.length&&(n.lastIndex=d,l=n.exec(i),null!==l);)d=n.lastIndex,n===M?"!--"===l[1]?n=H:void 0!==l[1]?n=N:void 0!==l[2]?(B.test(l[2])&&(o=RegExp("</"+l[2],"g")),n=U):void 0!==l[3]&&(n=U):n===U?">"===l[0]?(n=o??M,c=-1):void 0===l[1]?c=-2:(c=n.lastIndex-l[2].length,a=l[1],n=void 0===l[3]?U:'"'===l[3]?L:j):n===L||n===j?n=U:n===H||n===N?n=M:(n=U,o=void 0);const p=n===U&&t[e+1].startsWith("/>")?" ":"";r+=n===M?i+T:c>=0?(s.push(a),i.slice(0,c)+S+i.slice(c)+P+p):i+P+(-2===c?e:p)}return[V(t,r+(t[i]||"<?>")+(2===e?"</svg>":3===e?"</math>":"")),s]};class J{constructor({strings:t,_$litType$:e},i){let s;this.parts=[];let o=0,r=0;const n=t.length-1,a=this.parts,[l,c]=Z(t,e);if(this.el=J.createElement(l,i),q.currentNode=this.el.content,2===e||3===e){const t=this.el.content.firstChild;t.replaceWith(...t.childNodes)}for(;null!==(s=q.nextNode())&&a.length<n;){if(1===s.nodeType){if(s.hasAttributes())for(const t of s.getAttributeNames())if(t.endsWith(S)){const e=c[r++],i=s.getAttribute(t).split(P),n=/([.?@])?(.*)/.exec(e);a.push({type:1,index:o,name:n[2],strings:i,ctor:"."===n[1]?et:"?"===n[1]?it:"@"===n[1]?st:tt}),s.removeAttribute(t)}else t.startsWith(P)&&(a.push({type:6,index:o}),s.removeAttribute(t));if(B.test(s.tagName)){const t=s.textContent.split(P),e=t.length-1;if(e>0){s.textContent=A?A.emptyScript:"";for(let i=0;i<e;i++)s.append(t[i],F()),q.nextNode(),a.push({type:2,index:++o});s.append(t[e],F())}}}else if(8===s.nodeType)if(s.data===z)a.push({type:2,index:o});else{let t=-1;for(;-1!==(t=s.data.indexOf(P,t+1));)a.push({type:7,index:o}),t+=P.length-1}o++}}static createElement(t,e){const i=C.createElement("template");return i.innerHTML=t,i}}function Y(t,e,i=t,s){if(e===K)return e;let o=void 0!==s?i._$Co?.[s]:i._$Cl;const r=O(e)?void 0:e._$litDirective$;return o?.constructor!==r&&(o?._$AO?.(!1),void 0===r?o=void 0:(o=new r(t),o._$AT(t,i,s)),void 0!==s?(i._$Co??=[])[s]=o:i._$Cl=o),void 0!==o&&(e=Y(t,o._$AS(t,e.values),o,s)),e}class Q{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){const{el:{content:e},parts:i}=this._$AD,s=(t?.creationScope??C).importNode(e,!0);q.currentNode=s;let o=q.nextNode(),r=0,n=0,a=i[0];for(;void 0!==a;){if(r===a.index){let e;2===a.type?e=new X(o,o.nextSibling,this,t):1===a.type?e=new a.ctor(o,a.name,a.strings,this,t):6===a.type&&(e=new ot(o,this,t)),this._$AV.push(e),a=i[++n]}r!==a?.index&&(o=q.nextNode(),r++)}return q.currentNode=C,s}p(t){let e=0;for(const i of this._$AV)void 0!==i&&(void 0!==i.strings?(i._$AI(t,i,e),e+=i.strings.length-2):i._$AI(t[e])),e++}}class X{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,i,s){this.type=2,this._$AH=W,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=i,this.options=s,this._$Cv=s?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===t?.nodeType&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=Y(this,t,e),O(t)?t===W||null==t||""===t?(this._$AH!==W&&this._$AR(),this._$AH=W):t!==this._$AH&&t!==K&&this._(t):void 0!==t._$litType$?this.$(t):void 0!==t.nodeType?this.T(t):(t=>R(t)||"function"==typeof t?.[Symbol.iterator])(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==W&&O(this._$AH)?this._$AA.nextSibling.data=t:this.T(C.createTextNode(t)),this._$AH=t}$(t){const{values:e,_$litType$:i}=t,s="number"==typeof i?this._$AC(t):(void 0===i.el&&(i.el=J.createElement(V(i.h,i.h[0]),this.options)),i);if(this._$AH?._$AD===s)this._$AH.p(e);else{const t=new Q(s,this),i=t.u(this.options);t.p(e),this.T(i),this._$AH=t}}_$AC(t){let e=G.get(t.strings);return void 0===e&&G.set(t.strings,e=new J(t)),e}k(t){R(this._$AH)||(this._$AH=[],this._$AR());const e=this._$AH;let i,s=0;for(const o of t)s===e.length?e.push(i=new X(this.O(F()),this.O(F()),this,this.options)):i=e[s],i._$AI(o),s++;s<e.length&&(this._$AR(i&&i._$AB.nextSibling,s),e.length=s)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){const e=w(t).nextSibling;w(t).remove(),t=e}}setConnected(t){void 0===this._$AM&&(this._$Cv=t,this._$AP?.(t))}}class tt{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,i,s,o){this.type=1,this._$AH=W,this._$AN=void 0,this.element=t,this.name=e,this._$AM=s,this.options=o,i.length>2||""!==i[0]||""!==i[1]?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=W}_$AI(t,e=this,i,s){const o=this.strings;let r=!1;if(void 0===o)t=Y(this,t,e,0),r=!O(t)||t!==this._$AH&&t!==K,r&&(this._$AH=t);else{const s=t;let n,a;for(t=o[0],n=0;n<o.length-1;n++)a=Y(this,s[i+n],e,n),a===K&&(a=this._$AH[n]),r||=!O(a)||a!==this._$AH[n],a===W?t=W:t!==W&&(t+=(a??"")+o[n+1]),this._$AH[n]=a}r&&!s&&this.j(t)}j(t){t===W?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}}class et extends tt{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===W?void 0:t}}class it extends tt{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==W)}}class st extends tt{constructor(t,e,i,s,o){super(t,e,i,s,o),this.type=5}_$AI(t,e=this){if((t=Y(this,t,e,0)??W)===K)return;const i=this._$AH,s=t===W&&i!==W||t.capture!==i.capture||t.once!==i.once||t.passive!==i.passive,o=t!==W&&(i===W||s);s&&this.element.removeEventListener(this.name,this,i),o&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){"function"==typeof this._$AH?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}}class ot{constructor(t,e,i){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(t){Y(this,t)}}const rt=k.litHtmlPolyfillSupport;rt?.(J,X),(k.litHtmlVersions??=[]).push("3.3.3");const nt=globalThis;let at=class extends ${constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){const t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=((t,e,i)=>{const s=i?.renderBefore??e;let o=s._$litPart$;if(void 0===o){const t=i?.renderBefore??null;s._$litPart$=o=new X(e.insertBefore(F(),t),t,void 0,i??{})}return o._$AI(t),o})(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return K}};at._$litElement$=!0,at.finalized=!0,nt.litElementHydrateSupport?.({LitElement:at});const lt=nt.litElementPolyfillSupport;lt?.({LitElement:at}),(nt.litElementVersions??=[]).push("4.2.2");const ct=t=>(e,i)=>{void 0!==i?i.addInitializer(()=>{customElements.define(t,e)}):customElements.define(t,e)},dt={attribute:!0,type:String,converter:v,reflect:!1,hasChanged:b},pt=(t=dt,e,i)=>{const{kind:s,metadata:o}=i;let r=globalThis.litPropertyMetadata.get(o);if(void 0===r&&globalThis.litPropertyMetadata.set(o,r=new Map),"setter"===s&&((t=Object.create(t)).wrapped=!0),r.set(i.name,t),"accessor"===s){const{name:s}=i;return{set(i){const o=e.get.call(this);e.set.call(this,i),this.requestUpdate(s,o,t,!0,i)},init(e){return void 0!==e&&this.C(s,void 0,t,e),e}}}if("setter"===s){const{name:s}=i;return function(i){const o=this[s];e.call(this,i),this.requestUpdate(s,o,t,!0,i)}}throw Error("Unsupported decorator location: "+s)};function ht(t){return(e,i)=>"object"==typeof i?pt(t,e,i):((t,e,i)=>{const s=e.hasOwnProperty(i);return e.constructor.createProperty(i,t),s?Object.getOwnPropertyDescriptor(e,i):void 0})(t,e,i)}function ut(t){return ht({...t,state:!0,attribute:!1})}const _t=1;class gt{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,e,i){this._$Ct=t,this._$AM=e,this._$Ci=i}_$AS(t,e){return this.update(t,e)}update(t,e){return this.render(...e)}}const mt=(t=>(...e)=>({_$litDirective$:t,values:e}))(class extends gt{constructor(t){if(super(t),t.type!==_t||"class"!==t.name||t.strings?.length>2)throw Error("`classMap()` can only be used in the `class` attribute and must be the only part in the attribute.")}render(t){return" "+Object.keys(t).filter(e=>t[e]).join(" ")+" "}update(t,[e]){if(void 0===this.st){this.st=new Set,void 0!==t.strings&&(this.nt=new Set(t.strings.join(" ").split(/\s/).filter(t=>""!==t)));for(const t in e)e[t]&&!this.nt?.has(t)&&this.st.add(t);return this.render(e)}const i=t.element.classList;for(const t of this.st)t in e||(i.remove(t),this.st.delete(t));for(const t in e){const s=!!e[t];s===this.st.has(t)||this.nt?.has(t)||(s?(i.add(t),this.st.add(t)):(i.remove(t),this.st.delete(t)))}return K}});let ft=class extends at{setConfig(t){this._config={...t,entities:{...t.entities,open_tasks:t.entities?.open_tasks??""}}}_emit(t){this._config=t,this.dispatchEvent(new CustomEvent("config-changed",{detail:{config:t},bubbles:!0,composed:!0}))}_setGlobal(t,e){this._emit({...this._config,entities:{...this._config.entities,[t]:e}})}_setRoot(t,e){this._emit({...this._config,[t]:e})}_setPerson(t,e){const i=[...this._config.persons??[]];i[t]={...i[t],...e},this._emit({...this._config,persons:i})}_addPerson(){this._emit({...this._config,persons:[...this._config.persons??[],{entity:""}]})}_removePerson(t){const e=[...this._config.persons??[]];e.splice(t,1),this._emit({...this._config,persons:e})}_sensorPicker(t,e,i,s=["sensor"]){return customElements.get("ha-entity-picker")?I`<ha-entity-picker
        .hass=${this.hass}
        .label=${t}
        .value=${e??""}
        .includeDomains=${s}
        allow-custom-entity
        @value-changed=${t=>i(t.detail.value)}
      ></ha-entity-picker>`:I`<label class="row"><span>${t}</span><input .value=${e??""} @input=${t=>i(t.target.value)} /></label>`}render(){if(!this._config||!this.hass)return I``;const t=this._config.entities;return I`
      <div class="form">
        <label class="row"><span>Titel</span><input .value=${this._config.title??""} @input=${t=>this._setRoot("title",t.target.value)} /></label>

        <h4>Globale Sensoren</h4>
        ${this._sensorPicker("Offene Aufgaben (Pflicht)",t.open_tasks,t=>this._setGlobal("open_tasks",t))}
        ${this._sensorPicker("Fällige Aufgaben",t.due_tasks,t=>this._setGlobal("due_tasks",t))}
        ${this._sensorPicker("Überfällige Aufgaben",t.overdue_tasks,t=>this._setGlobal("overdue_tasks",t))}
        ${this._sensorPicker("Heute erledigt",t.completed_today,t=>this._setGlobal("completed_today",t))}
        ${this._sensorPicker("Diese Woche erledigt",t.completed_this_week,t=>this._setGlobal("completed_this_week",t))}
        ${this._sensorPicker("Aktive Ketten",t.active_chains,t=>this._setGlobal("active_chains",t))}

        <h4>Personen</h4>
        ${(this._config.persons??[]).map((t,e)=>I`
            <div class="person">
              <div class="person-head">
                ${this._sensorPicker("Person",t.entity,t=>this._setPerson(e,{entity:t}),["person"])}
                <button class="del" @click=${()=>this._removePerson(e)} title="Entfernen">✕</button>
              </div>
              ${this._sensorPicker("Offen",t.open_tasks,t=>this._setPerson(e,{open_tasks:t}))}
              ${this._sensorPicker("Fällig",t.due_tasks,t=>this._setPerson(e,{due_tasks:t}))}
              ${this._sensorPicker("Heute erledigt",t.completed_today,t=>this._setPerson(e,{completed_today:t}))}
              ${this._sensorPicker("Verbleibend heute",t.remaining_today,t=>this._setPerson(e,{remaining_today:t}))}
              ${this._sensorPicker("Hat fällige Aufgaben",t.has_due_tasks,t=>this._setPerson(e,{has_due_tasks:t}),["binary_sensor"])}
              ${this._sensorPicker("Kette aktiv",t.chain_active,t=>this._setPerson(e,{chain_active:t}),["binary_sensor"])}
            </div>`)}
        <button class="add" @click=${this._addPerson}>+ Person hinzufügen</button>

        <h4>Optionen</h4>
        <label class="check"><input type="checkbox" .checked=${!1!==this._config.show_create} @change=${t=>this._setRoot("show_create",t.target.checked)} />Erstellen-Dialog anzeigen</label>
        <label class="check"><input type="checkbox" .checked=${!1!==this._config.show_history} @change=${t=>this._setRoot("show_history",t.target.checked)} />Verlauf-Tab anzeigen</label>
        ${this._sensorPicker("Standard-Person",this._config.default_person,t=>this._setRoot("default_person",t),["person"])}
      </div>
    `}};ft.styles=n`
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
  `,t([ht({attribute:!1})],ft.prototype,"hass",void 0),t([ut()],ft.prototype,"_config",void 0),ft=t([ct("choreflow-card-editor")],ft);let yt=class extends at{constructor(){super(...arguments),this._tab="tasks",this._personFilter="all",this._roomFilter="all",this._categoryFilter="all",this._groupByRoom=!1,this._dialogOpen=!1,this._personPickerOpen=!1,this._pendingAction=null,this._rowState={},this._rowError={},this._tasks=null,this._tasksLoading=!1,this._tasksError=null,this._taskRequestGeneration=0,this._editForm=null,this._editSaving=!1,this._history=[],this._historyTotal=0,this._historyLoading=!1,this._historyOffset=0}static getConfigElement(){return document.createElement("choreflow-card-editor")}static getStubConfig(){return{title:"Haushalt",entities:{open_tasks:"sensor.choreflow_open_tasks",due_tasks:"sensor.choreflow_due_tasks",overdue_tasks:"sensor.choreflow_overdue_tasks",completed_today:"sensor.choreflow_completed_today",completed_this_week:"sensor.choreflow_completed_this_week",active_chains:"sensor.choreflow_active_chains"},persons:[],show_create:!0,show_history:!0}}setConfig(t){if(!t||!t.entities||!t.entities.open_tasks)throw new Error("choreflow-card: 'entities.open_tasks' ist erforderlich (z. B. sensor.choreflow_open_tasks).");this._config={show_create:!0,show_history:!0,...t,persons:t.persons??[]},this._personFilter=t.default_person??"all",this._roomFilter=t.default_room??"all",this._categoryFilter="all",this._tasks=null,this._tasksError=null,this._taskRequestGeneration+=1}getCardSize(){return 6}updated(t){const e=t.get("hass"),i=t.get("_config"),s=i?.entities.open_tasks??this._config?.entities.open_tasks,o=t.has("_config"),r=t.has("hass")&&(s?e?.states[s]:void 0)!==this._openSensor;this.hass&&this._config&&(o||r)&&this._loadTasks(o||null===this._tasks),"history"===this._tab&&this._config?.show_history&&0===this._history.length&&!this._historyLoading&&0===this._historyOffset&&this._loadHistory(!0)}get _openSensor(){const t=this._config?.entities.open_tasks;return t?this.hass?.states[t]:void 0}_openTasks(){const t=this._openSensor?.attributes?.open_tasks;return Array.isArray(t)?t:[]}_baseTasks(){return null!==this._tasks?this._tasks:"all"===this._personFilter?this._openTasks():[]}async _setPersonFilter(t){t===this._personFilter&&null!==this._tasks||(this._personFilter=t,this._roomFilter="all",this._categoryFilter="all",this._tasks=null,this._tasksError=null,await this._loadTasks(!0))}_retryTasks(){this._loadTasks(null===this._tasks)}async _loadTasks(t){const e=++this._taskRequestGeneration,i=t?null:this._tasks;t&&(this._tasks=null),this._tasksLoading=!0,this._tasksError=null;const s="all"===this._personFilter?void 0:this._personFilter,o=[];let r=0;try{for(;;){const t={status:"open",person_scope:"visible",limit:100,offset:r};s&&(t.person_entity=s);const e=await this.hass.connection.sendMessagePromise({type:"call_service",domain:"choreflow",service:"get_tasks",service_data:t,return_response:!0}),i=this._validateTaskPage(e?.response);if(o.push(...i.items),!i.has_more)break;if(0===i.items.length)throw new Error("get_tasks returned an empty page with has_more=true");r+=i.items.length}if(e!==this._taskRequestGeneration)return;this._tasks=o}catch(t){if(e!==this._taskRequestGeneration)return;console.error("[choreflow] get_tasks",t),this._tasks=i,this._tasksError="Aufgaben konnten nicht geladen werden."}finally{e===this._taskRequestGeneration&&(this._tasksLoading=!1)}}_validateTaskPage(t){if(!t||"object"!=typeof t)throw new Error("Invalid get_tasks response");const e=t;if(!Array.isArray(e.items)||"boolean"!=typeof e.has_more)throw new Error("Invalid get_tasks page");if(!e.items.every(t=>this._isTask(t)))throw new Error("Invalid task in get_tasks page");return{items:e.items,has_more:e.has_more}}_isTask(t){if(!t||"object"!=typeof t)return!1;const e=t;return!("string"!=typeof e.task_id||"string"!=typeof e.title||"string"!=typeof e.room||"string"!=typeof e.category||"low"!==e.importance&&"normal"!==e.importance&&"high"!==e.importance||null!=e.estimated_duration_minutes&&"number"!=typeof e.estimated_duration_minutes||null!=e.due_date&&"string"!=typeof e.due_date||null!=e.snooze_until&&"string"!=typeof e.snooze_until)}_num(t){if(!t)return null;const e=this.hass?.states[t];if(!e||"unknown"===e.state||"unavailable"===e.state)return null;const i=Number(e.state);return Number.isFinite(i)?i:null}_personName(t){const e=this.hass?.states[t.entity];return e?.attributes?.friendly_name||t.entity.split(".").pop()||t.entity}_dueInfo(t){if(!t)return{label:"Kein Termin",overdueDays:0,isOverdue:!1,isToday:!1,rank:100};const e=new Date;e.setHours(0,0,0,0);const i=new Date(t+"T00:00:00"),s=Math.round((i.getTime()-e.getTime())/864e5);if(s<0){const t=-s;return{label:1===t?"Gestern":`vor ${t} Tagen`,overdueDays:t,isOverdue:!0,isToday:!1,rank:1e3+t}}return 0===s?{label:"Heute",overdueDays:0,isOverdue:!1,isToday:!0,rank:600}:1===s?{label:"Morgen",overdueDays:0,isOverdue:!1,isToday:!1,rank:300}:{label:i.toLocaleDateString("de-DE",{weekday:"short",day:"2-digit",month:"2-digit"}),overdueDays:0,isOverdue:!1,isToday:!1,rank:200}}_relTime(t){const e=new Date(t),i=new Date,s=e.toDateString()===i.toDateString(),o=new Date(i);o.setDate(i.getDate()-1);const r=e.toLocaleTimeString("de-DE",{hour:"2-digit",minute:"2-digit"});return s?`Heute ${r}`:e.toDateString()===o.toDateString()?`Gestern ${r}`:e.toLocaleDateString("de-DE",{weekday:"short",day:"2-digit",month:"2-digit"})}_defaultPerson(){return this._config.default_person??("all"!==this._personFilter?this._personFilter:void 0)??this._config.persons?.[0]?.entity}_availablePersonsForPicker(){return this._config.persons?.length?this._config.persons.map(t=>({entity:t.entity,name:this._personName(t)})):Object.keys(this.hass.states).filter(t=>t.startsWith("person.")).map(t=>({entity:t,name:this.hass.states[t].attributes?.friendly_name||t.split(".").pop()||t}))}async _completeTask(t){if("pending"===this._rowState[t]||"done"===this._rowState[t])return;const e=this._defaultPerson();if(!e)return this._pendingAction={taskId:t,action:"complete"},void(this._personPickerOpen=!0);await this._executeComplete(t,e)}async _executeComplete(t,e){this._setRow(t,"pending"),this._clearRowError(t);try{await this.hass.callService("choreflow","complete_task",{task_id:t,person_entity:e,source:"dashboard"}),this._setRow(t,"done")}catch(e){this._setRow(t,"idle"),this._setRowError(t,this._friendlyError(e))}}async _snoozeTask(t){if("pending"===this._rowState[t]||"snoozed"===this._rowState[t])return;const e=this._defaultPerson();if(!e)return this._pendingAction={taskId:t,action:"snooze"},void(this._personPickerOpen=!0);await this._executeSnooze(t,e)}async _executeSnooze(t,e){this._setRow(t,"pending"),this._clearRowError(t);try{await this.hass.callService("choreflow","snooze_task",{task_id:t,person_entity:e}),this._setRow(t,"snoozed")}catch(e){this._setRow(t,"idle"),this._setRowError(t,this._friendlyError(e))}}async _reopenTask(t){try{await this.hass.callService("choreflow","reopen_task",{task_id:t}),await this._loadHistory(!0)}catch(t){console.error("[choreflow] reopen_task",t)}}async _openEdit(t){const e=await this.hass.connection.sendMessagePromise({type:"call_service",domain:"choreflow",service:"get_task",service_data:{task_id:t},return_response:!0}),i=e?.response;i&&(this._editForm={task_id:t,task_rule_id:i.task_rule_id??null,title:i.title??"",description:i.description??"",room:i.room??"",category:i.category??"",importance:i.importance??"normal",due_date:i.due_date??"",estimated_duration_minutes:null!=i.estimated_duration_minutes?String(i.estimated_duration_minutes):"",recurrence_type:i.recurrence_type??"once",recurrence_interval:null!=i.recurrence_interval?String(i.recurrence_interval):"1",recurrence_weekdays:i.recurrence_weekdays??[]})}_closeEdit(){this._editForm=null,this._editSaving=!1}_setEditField(t,e){this._editForm&&(this._editForm={...this._editForm,[t]:e})}_toggleEditWeekday(t){if(!this._editForm)return;const e=this._editForm.recurrence_weekdays,i=e.includes(t)?e.filter(e=>e!==t):[...e,t];this._editForm={...this._editForm,recurrence_weekdays:i}}async _saveEdit(){if(!this._editForm||this._editSaving)return;this._editSaving=!0;const t=this._editForm,e={task_id:t.task_id,title:t.title,description:t.description.trim()||null,room:t.room||void 0,category:t.category||void 0,importance:t.importance,due_date:t.due_date||null,estimated_duration_minutes:t.estimated_duration_minutes?Number(t.estimated_duration_minutes):null};t.task_rule_id&&(e.recurrence_type=t.recurrence_type,"every_n_days"===t.recurrence_type?e.recurrence_interval=Number(t.recurrence_interval)||1:"weekdays"===t.recurrence_type&&(e.recurrence_weekdays=t.recurrence_weekdays));try{await this.hass.callService("choreflow","update_task",e),this._closeEdit()}catch(t){console.error("[choreflow] update_task",t),this._editSaving=!1}}async _createTask(t){const e=await this.hass.connection.sendMessagePromise({type:"call_service",domain:"choreflow",service:"create_task",service_data:t,return_response:!0});return e?.response??{}}async _loadHistory(t=!1){if(!this._config.show_history)return;this._historyLoading=!0;const e=t?0:this._historyOffset;try{const i=await this.hass.connection.sendMessagePromise({type:"call_service",domain:"choreflow",service:"get_history",service_data:{limit:10,offset:e},return_response:!0}),s=i?.response;s&&(this._history=t?s.items:[...this._history,...s.items],this._historyTotal=s.total,this._historyOffset=e+s.items.length)}catch(t){console.error("[choreflow] get_history",t)}finally{this._historyLoading=!1}}_friendlyError(t){const e=t?.message??"";return/visib|sicht/i.test(e)?"Aufgabe ist dir nicht sichtbar.":/assign|zuweis/i.test(e)?"Aufgabe ist dir nicht zugewiesen.":/not open|nicht offen|unknown|unbekannt/i.test(e)?"Aufgabe ist nicht mehr offen.":/person/i.test(e)?"Person ist nicht aktiviert.":"Aktion fehlgeschlagen."}_setRow(t,e){this._rowState={...this._rowState,[t]:e}}_setRowError(t,e){this._rowError={...this._rowError,[t]:e},window.setTimeout(()=>this._clearRowError(t),5e3)}_clearRowError(t){if(!this._rowError[t])return;const e={...this._rowError};delete e[t],this._rowError=e}_localDate(t=new Date){return`${t.getFullYear()}-${String(t.getMonth()+1).padStart(2,"0")}-${String(t.getDate()).padStart(2,"0")}`}_isSnoozed(t){const e=this._localDate();return"snoozed"===this._rowState[t.task_id]||!!t.snooze_until&&t.snooze_until>e}_visibleTasks(){let t=this._baseTasks().filter(t=>"done"!==this._rowState[t.task_id]);return"all"!==this._roomFilter&&(t=t.filter(t=>t.room===this._roomFilter)),"all"!==this._categoryFilter&&(t=t.filter(t=>t.category===this._categoryFilter)),t.slice().sort((t,e)=>{const i=this._isSnoozed(t);return i!==this._isSnoozed(e)?i?1:-1:this._dueInfo(e.due_date).rank+vt(e.importance)-(this._dueInfo(t.due_date).rank+vt(t.importance))})}_rooms(){return[...new Set(this._baseTasks().map(t=>t.room).filter(Boolean))]}_categories(){return[...new Set(this._baseTasks().map(t=>t.category).filter(Boolean))]}render(){if(!this._config||!this.hass)return I``;if(!this._openSensor)return I`<ha-card>
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
      </ha-card>`;const t=this._num(this._config.entities.open_tasks)??this._openTasks().length,e=this._num(this._config.entities.due_tasks),i=this._num(this._config.entities.overdue_tasks),s=this._num(this._config.entities.completed_today);return I`
      <ha-card>
        <div class="head">
          <div class="title">
            <span class="title-text">${this._config.title??"ChoreFlow"}</span>
            <span class="sub">${t} offen</span>
          </div>
          <div class="head-actions">
            ${this._config.show_history?I`<div class="seg" role="tablist">
                  <button role="tab" class=${mt({on:"tasks"===this._tab})} @click=${()=>this._tab="tasks"}>Aufgaben</button>
                  <button role="tab" class=${mt({on:"history"===this._tab})} @click=${()=>this._tab="history"}>Verlauf</button>
                </div>`:W}
            ${this._config.show_create?I`<button class="icon-btn primary" aria-label="Aufgabe erstellen" title="Aufgabe erstellen" @click=${()=>this._dialogOpen=!0}>
                  <ha-icon icon="mdi:plus"></ha-icon>
                </button>`:W}
          </div>
        </div>

        <div class="stats">
          ${this._stat(t,"Offen")} ${this._stat(e,"Fällig")}
          ${this._stat(i,"Überfällig",i&&i>0?"error":"")}
          ${this._stat(s,"Heute erledigt")}
        </div>

        ${"tasks"===this._tab?this._renderTasks():this._renderHistory()}
      </ha-card>

      ${this._dialogOpen?this._renderDialog():W}
      ${this._personPickerOpen?this._renderPersonPicker():W}
      ${this._editForm?this._renderEditDialog():W}
    `}_stat(t,e,i=""){return I`<div class="stat">
      <div class="stat-num ${i}">${t??"—"}</div>
      <div class="stat-label">${e}</div>
    </div>`}_renderTasks(){const t=this._visibleTasks(),e=this._rooms(),i=this._categories();return I`
      <div class="filters">
        <div class="seg">
          <button class=${mt({on:"all"===this._personFilter})} @click=${()=>{this._setPersonFilter("all")}}>Alle</button>
          ${(this._config.persons??[]).map(t=>I`<button class=${mt({on:this._personFilter===t.entity})} @click=${()=>{this._setPersonFilter(t.entity)}}>${this._personName(t)}</button>`)}
        </div>
        <select aria-label="Raum filtern" .value=${this._roomFilter} @change=${t=>this._roomFilter=t.target.value}>
          <option value="all">Alle Räume</option>
          ${e.map(t=>I`<option value=${t}>${t}</option>`)}
        </select>
        <select aria-label="Kategorie filtern" .value=${this._categoryFilter} @change=${t=>this._categoryFilter=t.target.value}>
          <option value="all">Alle Kategorien</option>
          ${i.map(t=>I`<option value=${t}>${t}</option>`)}
        </select>
        <button class=${mt({chiptoggle:!0,on:this._groupByRoom})} @click=${()=>this._groupByRoom=!this._groupByRoom}>
          <ha-icon icon="mdi:view-list"></ha-icon>Nach Raum
        </button>
      </div>

      ${this._tasksLoading?I`<div class="task-status"><span class="spin"><ha-icon icon="mdi:loading"></ha-icon></span>${null===this._tasks?"Aufgaben werden geladen …":"Aufgaben werden aktualisiert …"}</div>`:W}
      ${this._tasksError?I`<div class="task-status task-error">
            <ha-icon icon="mdi:alert-outline"></ha-icon>
            <span>${this._tasksError}</span>
            <button type="button" @click=${()=>this._retryTasks()}>Erneut versuchen</button>
          </div>`:W}

      ${0===t.length&&(this._tasksLoading||this._tasksError)?W:0===t.length?I`<div class="empty"><ha-icon icon="mdi:check"></ha-icon><p>Für diesen Filter ist nichts offen.</p></div>`:this._groupByRoom?this._groupTasks(t):I`<div class="list">${t.map(t=>this._renderRow(t))}</div>`}
    `}_groupTasks(t){const e=new Map;for(const i of t){const t=i.room||"Ohne Raum";e.has(t)||e.set(t,[]),e.get(t).push(i)}return I`<div class="list">
      ${[...e.entries()].map(([t,e])=>I`
          <div class="group-head"><ha-icon icon="mdi:map-marker"></ha-icon>${t}<span class="group-count">· ${e.length}</span></div>
          ${e.map(t=>this._renderRow(t))}
        `)}
    </div>`}_renderRow(t){const e=this._dueInfo(t.due_date),i=t.due_date?Math.round((new Date(t.due_date+"T00:00:00").getTime()-(new Date).setHours(0,0,0,0))/864e5):null;let s="normal";e.isOverdue?s="overdue":"high"===t.importance?s="high":e.isToday&&(s="today");let o="",r="";e.isOverdue?(o="mdi:alert",r=`Überfällig · ${e.overdueDays} ${1===e.overdueDays?"Tag":"Tage"}`):e.isToday&&"high"===t.importance?(o="mdi:alert-circle",r="Heute fällig · Wichtig"):e.isToday?(o="mdi:clock-outline",r="Heute fällig"):"high"===t.importance&&null!==i&&i<=2&&(o="mdi:chevron-up",r=1===i?"Morgen fällig · Wichtig":"Bald fällig · Wichtig");const n=this._rowState[t.task_id]??"idle",a=this._isSnoozed(t),l=this._rowError[t.task_id],c=!!t.task_id,d=[t.room,t.category];return t.estimated_duration_minutes&&d.push(`${t.estimated_duration_minutes} Min`),I`<div class=${mt({row:!0,[s]:!0,settled:"done"===n,"row-snoozed":a})}>
      <div class="row-main">
        <div class="row-top">
          <span class="row-title ${"done"===n?"struck":""}">${t.title}</span>
          <span class="due ${s}">${e.label}</span>
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
              <button class="icon-btn ok" aria-label="Erledigen" title="Erledigen" @click=${()=>this._completeTask(t.task_id)}>
                <ha-icon icon="mdi:check-circle"></ha-icon>
              </button>
            `:c?I`
              <button class="icon-btn" aria-label="Bearbeiten" title="Bearbeiten" @click=${()=>this._openEdit(t.task_id)}>
                <ha-icon icon="mdi:pencil"></ha-icon>
              </button>
              <button class="icon-btn" aria-label="Später erinnern" title="Später erinnern" @click=${()=>this._snoozeTask(t.task_id)}>
                <ha-icon icon="mdi:clock-outline"></ha-icon>
              </button>
              <button class="icon-btn ok" aria-label="Erledigen" title="Erledigen" @click=${()=>this._completeTask(t.task_id)}>
                <ha-icon icon="mdi:check-circle"></ha-icon>
              </button>
            `:W}
      </div>
    </div>`}_renderHistory(){return I`
      <div class="hist-head">Verlauf</div>
      ${0===this._history.length&&this._historyLoading?I`<div class="empty"><p>Lädt…</p></div>`:0===this._history.length?I`<div class="empty"><p>Noch keine Einträge.</p></div>`:I`<div class="list">
            ${this._history.map(t=>{const e=function(t){switch(t){case"task_completed":return{icon:"mdi:check-circle",tone:"ok",label:"Erledigt"};case"task_completed_from_todo":return{icon:"mdi:clipboard-check",tone:"ok",label:"Erledigt (To-do)"};case"task_reopened":return{icon:"mdi:undo",tone:"warn",label:"Korrigiert"};case"task_snoozed":return{icon:"mdi:clock-outline",tone:"warn",label:"Später erinnert"};case"task_created":return{icon:"mdi:plus-circle-outline",tone:"muted",label:"Erstellt"};case"task_updated":return{icon:"mdi:pencil",tone:"muted",label:"Geändert"};case"task_deleted":return{icon:"mdi:delete-outline",tone:"muted",label:"Gelöscht"};case"task_notified":return{icon:"mdi:bell-outline",tone:"muted",label:"Benachrichtigt"};case"task_missed_no_presence":return{icon:"mdi:account-off-outline",tone:"err",label:"Verpasst (abwesend)"};case"task_expired":return{icon:"mdi:close-circle-outline",tone:"err",label:"Abgelaufen"};case"task_synced_from_todo":return{icon:"mdi:sync",tone:"muted",label:"Aus To-do"};case"calendar_task_created":return{icon:"mdi:calendar-plus",tone:"muted",label:"Kalender erstellt"};case"calendar_task_removed":return{icon:"mdi:calendar-remove",tone:"muted",label:"Kalender entfernt"};default:return{icon:"mdi:information-outline",tone:"muted",label:t}}}(t.event_type),i=("task_completed"===t.event_type||"task_completed_from_todo"===t.event_type)&&!!t.task_id,s=[e.label,t.room,t.person_entity?bt(this.hass,t.person_entity):null].filter(Boolean);return I`<div class="hist">
                <ha-icon class=${e.tone} icon=${e.icon}></ha-icon>
                <div class="hist-main">
                  <div class="hist-top">
                    <span class="hist-title">${t.title??"—"}</span>
                    <span class="hist-time">${this._relTime(t.timestamp)}</span>
                  </div>
                  <div class="hist-meta">${s.join(" · ")}</div>
                </div>
                ${i?I`<button class="icon-btn" aria-label="Korrigieren" title="Erledigung rückgängig machen" @click=${()=>this._reopenTask(t.task_id)}>
                      <ha-icon icon="mdi:undo"></ha-icon>
                    </button>`:W}
              </div>`})}
          </div>`}
      ${this._historyOffset<this._historyTotal?I`<button class="loadmore" ?disabled=${this._historyLoading} @click=${()=>this._loadHistory(!1)}>
            ${this._historyLoading?"Lädt…":"Mehr laden"}
          </button>`:W}
    `}_renderPersonPicker(){const t=this._availablePersonsForPicker(),e=()=>{this._personPickerOpen=!1,this._pendingAction=null},i=async t=>{this._personPickerOpen=!1;const e=this._pendingAction;this._pendingAction=null,e&&("complete"===e.action?await this._executeComplete(e.taskId,t):await this._executeSnooze(e.taskId,t))};return I`<div class="overlay" @click=${e}>
      <div class="dialog" style="max-width:320px" @click=${t=>t.stopPropagation()}>
        <div class="dlg-head">
          <span>Wer bist du?</span>
          <button type="button" class="icon-btn" aria-label="Schließen" @click=${e}><ha-icon icon="mdi:close"></ha-icon></button>
        </div>
        <div class="dlg-body">
          ${t.length?t.map(t=>I`<button class="person-pick-btn" @click=${()=>i(t.entity)}>${t.name}</button>`):I`<p style="margin:0;font-size:13px;color:var(--secondary-text-color)">Keine Personen gefunden. Bitte <code>persons</code> oder <code>default_person</code> in der Kartenkonfiguration setzen.</p>`}
        </div>
      </div>
    </div>`}_renderEditDialog(){const t=this._editForm,e=!!t.task_rule_id;return I`<div class="overlay" @click=${()=>this._closeEdit()}>
      <div class="dialog edit-dialog" @click=${t=>t.stopPropagation()}>
        <div class="dlg-head">
          <span>Aufgabe bearbeiten</span>
          <button type="button" class="icon-btn" aria-label="Schließen" @click=${()=>this._closeEdit()}>
            <ha-icon icon="mdi:close"></ha-icon>
          </button>
        </div>
        <div class="dlg-body edit-body">
          <label class="edit-label">Titel
            <input class="edit-input" type="text" .value=${t.title}
              @input=${t=>this._setEditField("title",t.target.value)} />
          </label>
          <label class="edit-label">Beschreibung
            <textarea class="edit-input edit-textarea" rows="2"
              @input=${t=>this._setEditField("description",t.target.value)}
            >${t.description}</textarea>
          </label>
          <div class="edit-row2">
            <label class="edit-label">Raum
              <input class="edit-input" type="text" .value=${t.room}
                @input=${t=>this._setEditField("room",t.target.value)} />
            </label>
            <label class="edit-label">Kategorie
              <input class="edit-input" type="text" .value=${t.category}
                @input=${t=>this._setEditField("category",t.target.value)} />
            </label>
          </div>
          <div class="edit-row2">
            <label class="edit-label">Wichtigkeit
              <select class="edit-input" .value=${t.importance}
                @change=${t=>this._setEditField("importance",t.target.value)}>
                <option value="high" ?selected=${"high"===t.importance}>Hoch</option>
                <option value="normal" ?selected=${"normal"===t.importance}>Normal</option>
                <option value="low" ?selected=${"low"===t.importance}>Niedrig</option>
              </select>
            </label>
            <label class="edit-label">Dauer (Min)
              <input class="edit-input" type="number" min="1" max="1440" .value=${t.estimated_duration_minutes}
                @input=${t=>this._setEditField("estimated_duration_minutes",t.target.value)} />
            </label>
          </div>
          <label class="edit-label">Fälligkeitsdatum
            <input class="edit-input" type="date" .value=${t.due_date}
              @change=${t=>this._setEditField("due_date",t.target.value)} />
          </label>
          ${e?I`
            <div class="edit-section-head">Wiederholung</div>
            <div class="edit-recurrence-btns">
              ${["once","every_n_days","weekdays"].map(e=>I`
                <button class=${mt({"recurrence-btn":!0,active:t.recurrence_type===e})}
                  type="button" @click=${()=>this._setEditField("recurrence_type",e)}>
                  ${{once:"Einmalig",every_n_days:"Alle N Tage",weekdays:"Wochentage"}[e]}
                </button>`)}
            </div>
            ${"every_n_days"===t.recurrence_type?I`
              <label class="edit-label">Intervall (Tage)
                <input class="edit-input" type="number" min="1" max="365" .value=${t.recurrence_interval}
                  @input=${t=>this._setEditField("recurrence_interval",t.target.value)} />
              </label>`:W}
            ${"weekdays"===t.recurrence_type?I`
              <div class="weekday-picker">
                ${["Mo","Di","Mi","Do","Fr","Sa","So"].map((e,i)=>I`
                  <button type="button"
                    class=${mt({"wd-btn":!0,active:t.recurrence_weekdays.includes(i)})}
                    @click=${()=>this._toggleEditWeekday(i)}>${e}</button>`)}
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
    </div>`}_renderDialog(){const t=this._rooms(),e=this._categories(),i=this._config.persons??[],s=()=>this._dialogOpen=!1;return I`<div class="overlay" @click=${s}>
      <form class="dialog" @click=${t=>t.stopPropagation()} @submit=${async t=>{t.preventDefault();const e=t.target.closest("form"),i=new FormData(e),o=String(i.get("title")??"").trim();if(!o)return void e.querySelector("[name=title]")?.focus();const r=String(i.get("visibility_mode")||"all_enabled_persons"),n=String(i.get("assignment_mode")||"random"),a=String(i.get("calendar_export_entity_id")||"").trim()||void 0,l={title:o,description:String(i.get("description")||"")||void 0,room:String(i.get("room")||"")||void 0,category:String(i.get("category")||"")||void 0,importance:String(i.get("importance")||"normal"),estimated_duration_minutes:i.get("duration")?Number(i.get("duration")):void 0,due_date:String(i.get("due_date")||"")||void 0,visibility_mode:r,visibility_persons:"selected_persons"===r?i.getAll("visibility_persons").map(String):void 0,assignment_mode:n,assignment_person:"assigned"===n&&String(i.get("assignment_person")||"")||void 0,calendar_export_entity_id:a};try{await this._createTask(l),s()}catch(t){console.error("[choreflow] create_task",t)}}}>
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
          <datalist id="cf-rooms">${t.map(t=>I`<option value=${t}></option>`)}</datalist>
          <datalist id="cf-cats">${e.map(t=>I`<option value=${t}></option>`)}</datalist>
          <fieldset class="radios">
            <legend>Wichtigkeit</legend>
            ${["low","normal","high"].map((t,e)=>I`<label class="radio"><input type="radio" name="importance" value=${t} ?checked=${1===e} />${{low:"Niedrig",normal:"Normal",high:"Hoch"}[t]}</label>`)}
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
                  ${i.map(t=>I`<label class="chip-check"><input type="checkbox" name="visibility_persons" value=${t.entity} />${this._personName(t)}</label>`)}
                </div>`:W}
            <fieldset class="radios">
              <legend>Zuweisung</legend>
              <label class="radio"><input type="radio" name="assignment_mode" value="random" checked />Zufällig</label>
              <label class="radio"><input type="radio" name="assignment_mode" value="assigned" />Feste Person</label>
            </fieldset>
            <label>Person<select name="assignment_person">
              <option value="">Person wählen…</option>
              ${i.map(t=>I`<option value=${t.entity}>${this._personName(t)}</option>`)}
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
    </div>`}};function vt(t){return"high"===t?40:"low"===t?-20:0}function bt(t,e){const i=t.states[e];return i?.attributes?.friendly_name||e.split(".").pop()||e}yt.styles=n`
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
  `,t([ht({attribute:!1})],yt.prototype,"hass",void 0),t([ut()],yt.prototype,"_config",void 0),t([ut()],yt.prototype,"_tab",void 0),t([ut()],yt.prototype,"_personFilter",void 0),t([ut()],yt.prototype,"_roomFilter",void 0),t([ut()],yt.prototype,"_categoryFilter",void 0),t([ut()],yt.prototype,"_groupByRoom",void 0),t([ut()],yt.prototype,"_dialogOpen",void 0),t([ut()],yt.prototype,"_personPickerOpen",void 0),t([ut()],yt.prototype,"_pendingAction",void 0),t([ut()],yt.prototype,"_rowState",void 0),t([ut()],yt.prototype,"_rowError",void 0),t([ut()],yt.prototype,"_tasks",void 0),t([ut()],yt.prototype,"_tasksLoading",void 0),t([ut()],yt.prototype,"_tasksError",void 0),t([ut()],yt.prototype,"_editForm",void 0),t([ut()],yt.prototype,"_editSaving",void 0),t([ut()],yt.prototype,"_history",void 0),t([ut()],yt.prototype,"_historyTotal",void 0),t([ut()],yt.prototype,"_historyLoading",void 0),t([ut()],yt.prototype,"_historyOffset",void 0),yt=t([ct("choreflow-card")],yt),window.customCards=window.customCards||[],window.customCards.push({type:"choreflow-card",name:"ChoreFlow Card",description:"Ruhige, kompakte Aufgaben-Card für die ChoreFlow-Integration.",preview:!0,documentationURL:"https://github.com/your-org/ha-choreflow-card"});export{yt as ChoreFlowCard};
