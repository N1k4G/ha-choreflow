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
function t(t,e,i,o){var r,s=arguments.length,n=s<3?e:null===o?o=Object.getOwnPropertyDescriptor(e,i):o;if("object"==typeof Reflect&&"function"==typeof Reflect.decorate)n=Reflect.decorate(t,e,i,o);else for(var a=t.length-1;a>=0;a--)(r=t[a])&&(n=(s<3?r(n):s>3?r(e,i,n):r(e,i))||n);return s>3&&n&&Object.defineProperty(e,i,n),n}"function"==typeof SuppressedError&&SuppressedError;const e=globalThis,i=e.ShadowRoot&&(void 0===e.ShadyCSS||e.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,o=Symbol(),r=new WeakMap;let s=class{constructor(t,e,i){if(this._$cssResult$=!0,i!==o)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o;const e=this.t;if(i&&void 0===t){const i=void 0!==e&&1===e.length;i&&(t=r.get(e)),void 0===t&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),i&&r.set(e,t))}return t}toString(){return this.cssText}};const n=(t,...e)=>{const i=1===t.length?t[0]:e.reduce((e,i,o)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+t[o+1],t[0]);return new s(i,t,o)},a=i?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const i of t.cssRules)e+=i.cssText;return(t=>new s("string"==typeof t?t:t+"",void 0,o))(e)})(t):t,{is:l,defineProperty:d,getOwnPropertyDescriptor:c,getOwnPropertyNames:h,getOwnPropertySymbols:p,getPrototypeOf:_}=Object,u=globalThis,g=u.trustedTypes,m=g?g.emptyScript:"",y=u.reactiveElementPolyfillSupport,f=(t,e)=>t,v={toAttribute(t,e){switch(e){case Boolean:t=t?m:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let i=t;switch(e){case Boolean:i=null!==t;break;case Number:i=null===t?null:Number(t);break;case Object:case Array:try{i=JSON.parse(t)}catch(t){i=null}}return i}},b=(t,e)=>!l(t,e),k={attribute:!0,type:String,converter:v,reflect:!1,useDefault:!1,hasChanged:b};Symbol.metadata??=Symbol("metadata"),u.litPropertyMetadata??=new WeakMap;let $=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=k){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){const i=Symbol(),o=this.getPropertyDescriptor(t,i,e);void 0!==o&&d(this.prototype,t,o)}}static getPropertyDescriptor(t,e,i){const{get:o,set:r}=c(this.prototype,t)??{get(){return this[e]},set(t){this[e]=t}};return{get:o,set(e){const s=o?.call(this);r?.call(this,e),this.requestUpdate(t,s,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??k}static _$Ei(){if(this.hasOwnProperty(f("elementProperties")))return;const t=_(this);t.finalize(),void 0!==t.l&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(f("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(f("properties"))){const t=this.properties,e=[...h(t),...p(t)];for(const i of e)this.createProperty(i,t[i])}const t=this[Symbol.metadata];if(null!==t){const e=litPropertyMetadata.get(t);if(void 0!==e)for(const[t,i]of e)this.elementProperties.set(t,i)}this._$Eh=new Map;for(const[t,e]of this.elementProperties){const i=this._$Eu(t,e);void 0!==i&&this._$Eh.set(i,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const i=new Set(t.flat(1/0).reverse());for(const t of i)e.unshift(a(t))}else void 0!==t&&e.push(a(t));return e}static _$Eu(t,e){const i=e.attribute;return!1===i?void 0:"string"==typeof i?i:"string"==typeof t?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),void 0!==this.renderRoot&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){const t=new Map,e=this.constructor.elementProperties;for(const i of e.keys())this.hasOwnProperty(i)&&(t.set(i,this[i]),delete this[i]);t.size>0&&(this._$Ep=t)}createRenderRoot(){const t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return((t,o)=>{if(i)t.adoptedStyleSheets=o.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(const i of o){const o=document.createElement("style"),r=e.litNonce;void 0!==r&&o.setAttribute("nonce",r),o.textContent=i.cssText,t.appendChild(o)}})(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,i){this._$AK(t,i)}_$ET(t,e){const i=this.constructor.elementProperties.get(t),o=this.constructor._$Eu(t,i);if(void 0!==o&&!0===i.reflect){const r=(void 0!==i.converter?.toAttribute?i.converter:v).toAttribute(e,i.type);this._$Em=t,null==r?this.removeAttribute(o):this.setAttribute(o,r),this._$Em=null}}_$AK(t,e){const i=this.constructor,o=i._$Eh.get(t);if(void 0!==o&&this._$Em!==o){const t=i.getPropertyOptions(o),r="function"==typeof t.converter?{fromAttribute:t.converter}:void 0!==t.converter?.fromAttribute?t.converter:v;this._$Em=o;const s=r.fromAttribute(e,t.type);this[o]=s??this._$Ej?.get(o)??s,this._$Em=null}}requestUpdate(t,e,i,o=!1,r){if(void 0!==t){const s=this.constructor;if(!1===o&&(r=this[t]),i??=s.getPropertyOptions(t),!((i.hasChanged??b)(r,e)||i.useDefault&&i.reflect&&r===this._$Ej?.get(t)&&!this.hasAttribute(s._$Eu(t,i))))return;this.C(t,e,i)}!1===this.isUpdatePending&&(this._$ES=this._$EP())}C(t,e,{useDefault:i,reflect:o,wrapped:r},s){i&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,s??e??this[t]),!0!==r||void 0!==s)||(this._$AL.has(t)||(this.hasUpdated||i||(e=void 0),this._$AL.set(t,e)),!0===o&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(const[t,e]of this._$Ep)this[t]=e;this._$Ep=void 0}const t=this.constructor.elementProperties;if(t.size>0)for(const[e,i]of t){const{wrapped:t}=i,o=this[e];!0!==t||this._$AL.has(e)||void 0===o||this.C(e,void 0,i,o)}}let t=!1;const e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(t=>t.hostUpdate?.()),this.update(e)):this._$EM()}catch(e){throw t=!1,this._$EM(),e}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(t=>this._$ET(t,this[t])),this._$EM()}updated(t){}firstUpdated(t){}};$.elementStyles=[],$.shadowRootOptions={mode:"open"},$[f("elementProperties")]=new Map,$[f("finalized")]=new Map,y?.({ReactiveElement:$}),(u.reactiveElementVersions??=[]).push("2.1.2");const x=globalThis,w=t=>t,A=x.trustedTypes,E=A?A.createPolicy("lit-html",{createHTML:t=>t}):void 0,S="$lit$",P=`lit$${Math.random().toFixed(9).slice(2)}$`,T="?"+P,z=`<${T}>`,C=document,R=()=>C.createComment(""),F=t=>null===t||"object"!=typeof t&&"function"!=typeof t,O=Array.isArray,D="[ \t\n\f\r]",N=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,M=/-->/g,H=/>/g,U=RegExp(`>|${D}(?:([^\\s"'>=/]+)(${D}*=${D}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),L=/'/g,j=/"/g,I=/^(?:script|style|textarea|title)$/i,B=(t=>(e,...i)=>({_$litType$:t,strings:e,values:i}))(1),W=Symbol.for("lit-noChange"),q=Symbol.for("lit-nothing"),G=new WeakMap,K=C.createTreeWalker(C,129);function V(t,e){if(!O(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==E?E.createHTML(e):e}const Z=(t,e)=>{const i=t.length-1,o=[];let r,s=2===e?"<svg>":3===e?"<math>":"",n=N;for(let e=0;e<i;e++){const i=t[e];let a,l,d=-1,c=0;for(;c<i.length&&(n.lastIndex=c,l=n.exec(i),null!==l);)c=n.lastIndex,n===N?"!--"===l[1]?n=M:void 0!==l[1]?n=H:void 0!==l[2]?(I.test(l[2])&&(r=RegExp("</"+l[2],"g")),n=U):void 0!==l[3]&&(n=U):n===U?">"===l[0]?(n=r??N,d=-1):void 0===l[1]?d=-2:(d=n.lastIndex-l[2].length,a=l[1],n=void 0===l[3]?U:'"'===l[3]?j:L):n===j||n===L?n=U:n===M||n===H?n=N:(n=U,r=void 0);const h=n===U&&t[e+1].startsWith("/>")?" ":"";s+=n===N?i+z:d>=0?(o.push(a),i.slice(0,d)+S+i.slice(d)+P+h):i+P+(-2===d?e:h)}return[V(t,s+(t[i]||"<?>")+(2===e?"</svg>":3===e?"</math>":"")),o]};class Y{constructor({strings:t,_$litType$:e},i){let o;this.parts=[];let r=0,s=0;const n=t.length-1,a=this.parts,[l,d]=Z(t,e);if(this.el=Y.createElement(l,i),K.currentNode=this.el.content,2===e||3===e){const t=this.el.content.firstChild;t.replaceWith(...t.childNodes)}for(;null!==(o=K.nextNode())&&a.length<n;){if(1===o.nodeType){if(o.hasAttributes())for(const t of o.getAttributeNames())if(t.endsWith(S)){const e=d[s++],i=o.getAttribute(t).split(P),n=/([.?@])?(.*)/.exec(e);a.push({type:1,index:r,name:n[2],strings:i,ctor:"."===n[1]?et:"?"===n[1]?it:"@"===n[1]?ot:tt}),o.removeAttribute(t)}else t.startsWith(P)&&(a.push({type:6,index:r}),o.removeAttribute(t));if(I.test(o.tagName)){const t=o.textContent.split(P),e=t.length-1;if(e>0){o.textContent=A?A.emptyScript:"";for(let i=0;i<e;i++)o.append(t[i],R()),K.nextNode(),a.push({type:2,index:++r});o.append(t[e],R())}}}else if(8===o.nodeType)if(o.data===T)a.push({type:2,index:r});else{let t=-1;for(;-1!==(t=o.data.indexOf(P,t+1));)a.push({type:7,index:r}),t+=P.length-1}r++}}static createElement(t,e){const i=C.createElement("template");return i.innerHTML=t,i}}function J(t,e,i=t,o){if(e===W)return e;let r=void 0!==o?i._$Co?.[o]:i._$Cl;const s=F(e)?void 0:e._$litDirective$;return r?.constructor!==s&&(r?._$AO?.(!1),void 0===s?r=void 0:(r=new s(t),r._$AT(t,i,o)),void 0!==o?(i._$Co??=[])[o]=r:i._$Cl=r),void 0!==r&&(e=J(t,r._$AS(t,e.values),r,o)),e}class Q{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){const{el:{content:e},parts:i}=this._$AD,o=(t?.creationScope??C).importNode(e,!0);K.currentNode=o;let r=K.nextNode(),s=0,n=0,a=i[0];for(;void 0!==a;){if(s===a.index){let e;2===a.type?e=new X(r,r.nextSibling,this,t):1===a.type?e=new a.ctor(r,a.name,a.strings,this,t):6===a.type&&(e=new rt(r,this,t)),this._$AV.push(e),a=i[++n]}s!==a?.index&&(r=K.nextNode(),s++)}return K.currentNode=C,o}p(t){let e=0;for(const i of this._$AV)void 0!==i&&(void 0!==i.strings?(i._$AI(t,i,e),e+=i.strings.length-2):i._$AI(t[e])),e++}}class X{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,i,o){this.type=2,this._$AH=q,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=i,this.options=o,this._$Cv=o?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===t?.nodeType&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=J(this,t,e),F(t)?t===q||null==t||""===t?(this._$AH!==q&&this._$AR(),this._$AH=q):t!==this._$AH&&t!==W&&this._(t):void 0!==t._$litType$?this.$(t):void 0!==t.nodeType?this.T(t):(t=>O(t)||"function"==typeof t?.[Symbol.iterator])(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==q&&F(this._$AH)?this._$AA.nextSibling.data=t:this.T(C.createTextNode(t)),this._$AH=t}$(t){const{values:e,_$litType$:i}=t,o="number"==typeof i?this._$AC(t):(void 0===i.el&&(i.el=Y.createElement(V(i.h,i.h[0]),this.options)),i);if(this._$AH?._$AD===o)this._$AH.p(e);else{const t=new Q(o,this),i=t.u(this.options);t.p(e),this.T(i),this._$AH=t}}_$AC(t){let e=G.get(t.strings);return void 0===e&&G.set(t.strings,e=new Y(t)),e}k(t){O(this._$AH)||(this._$AH=[],this._$AR());const e=this._$AH;let i,o=0;for(const r of t)o===e.length?e.push(i=new X(this.O(R()),this.O(R()),this,this.options)):i=e[o],i._$AI(r),o++;o<e.length&&(this._$AR(i&&i._$AB.nextSibling,o),e.length=o)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){const e=w(t).nextSibling;w(t).remove(),t=e}}setConnected(t){void 0===this._$AM&&(this._$Cv=t,this._$AP?.(t))}}class tt{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,i,o,r){this.type=1,this._$AH=q,this._$AN=void 0,this.element=t,this.name=e,this._$AM=o,this.options=r,i.length>2||""!==i[0]||""!==i[1]?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=q}_$AI(t,e=this,i,o){const r=this.strings;let s=!1;if(void 0===r)t=J(this,t,e,0),s=!F(t)||t!==this._$AH&&t!==W,s&&(this._$AH=t);else{const o=t;let n,a;for(t=r[0],n=0;n<r.length-1;n++)a=J(this,o[i+n],e,n),a===W&&(a=this._$AH[n]),s||=!F(a)||a!==this._$AH[n],a===q?t=q:t!==q&&(t+=(a??"")+r[n+1]),this._$AH[n]=a}s&&!o&&this.j(t)}j(t){t===q?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}}class et extends tt{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===q?void 0:t}}class it extends tt{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==q)}}class ot extends tt{constructor(t,e,i,o,r){super(t,e,i,o,r),this.type=5}_$AI(t,e=this){if((t=J(this,t,e,0)??q)===W)return;const i=this._$AH,o=t===q&&i!==q||t.capture!==i.capture||t.once!==i.once||t.passive!==i.passive,r=t!==q&&(i===q||o);o&&this.element.removeEventListener(this.name,this,i),r&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){"function"==typeof this._$AH?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}}class rt{constructor(t,e,i){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(t){J(this,t)}}const st=x.litHtmlPolyfillSupport;st?.(Y,X),(x.litHtmlVersions??=[]).push("3.3.3");const nt=globalThis;let at=class extends ${constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){const t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=((t,e,i)=>{const o=i?.renderBefore??e;let r=o._$litPart$;if(void 0===r){const t=i?.renderBefore??null;o._$litPart$=r=new X(e.insertBefore(R(),t),t,void 0,i??{})}return r._$AI(t),r})(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return W}};at._$litElement$=!0,at.finalized=!0,nt.litElementHydrateSupport?.({LitElement:at});const lt=nt.litElementPolyfillSupport;lt?.({LitElement:at}),(nt.litElementVersions??=[]).push("4.2.2");const dt=t=>(e,i)=>{void 0!==i?i.addInitializer(()=>{customElements.define(t,e)}):customElements.define(t,e)},ct={attribute:!0,type:String,converter:v,reflect:!1,hasChanged:b},ht=(t=ct,e,i)=>{const{kind:o,metadata:r}=i;let s=globalThis.litPropertyMetadata.get(r);if(void 0===s&&globalThis.litPropertyMetadata.set(r,s=new Map),"setter"===o&&((t=Object.create(t)).wrapped=!0),s.set(i.name,t),"accessor"===o){const{name:o}=i;return{set(i){const r=e.get.call(this);e.set.call(this,i),this.requestUpdate(o,r,t,!0,i)},init(e){return void 0!==e&&this.C(o,void 0,t,e),e}}}if("setter"===o){const{name:o}=i;return function(i){const r=this[o];e.call(this,i),this.requestUpdate(o,r,t,!0,i)}}throw Error("Unsupported decorator location: "+o)};function pt(t){return(e,i)=>"object"==typeof i?ht(t,e,i):((t,e,i)=>{const o=e.hasOwnProperty(i);return e.constructor.createProperty(i,t),o?Object.getOwnPropertyDescriptor(e,i):void 0})(t,e,i)}function _t(t){return pt({...t,state:!0,attribute:!1})}const ut=1;class gt{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,e,i){this._$Ct=t,this._$AM=e,this._$Ci=i}_$AS(t,e){return this.update(t,e)}update(t,e){return this.render(...e)}}const mt=(t=>(...e)=>({_$litDirective$:t,values:e}))(class extends gt{constructor(t){if(super(t),t.type!==ut||"class"!==t.name||t.strings?.length>2)throw Error("`classMap()` can only be used in the `class` attribute and must be the only part in the attribute.")}render(t){return" "+Object.keys(t).filter(e=>t[e]).join(" ")+" "}update(t,[e]){if(void 0===this.st){this.st=new Set,void 0!==t.strings&&(this.nt=new Set(t.strings.join(" ").split(/\s/).filter(t=>""!==t)));for(const t in e)e[t]&&!this.nt?.has(t)&&this.st.add(t);return this.render(e)}const i=t.element.classList;for(const t of this.st)t in e||(i.remove(t),this.st.delete(t));for(const t in e){const o=!!e[t];o===this.st.has(t)||this.nt?.has(t)||(o?(i.add(t),this.st.add(t)):(i.remove(t),this.st.delete(t)))}return W}}),yt={de:{"task.load_error":"Aufgaben konnten nicht geladen werden.","due.none":"Kein Termin","date.yesterday":"Gestern","date.days_ago":"vor {count} Tagen","date.today":"Heute","date.tomorrow":"Morgen","date.today_time":"Heute {time}","date.yesterday_time":"Gestern {time}","edit.duration_error":"Die Dauer muss eine ganze Zahl zwischen 1 und 1440 Minuten sein.","error.not_visible":"Aufgabe ist dir nicht sichtbar.","error.not_assigned":"Aufgabe ist dir nicht zugewiesen.","error.not_open":"Aufgabe ist nicht mehr offen.","error.person_disabled":"Person ist nicht aktiviert.","error.action_failed":"Aktion fehlgeschlagen.","card.unavailable":"ChoreFlow nicht verfügbar","card.sensor_missing":"Der Pflicht-Sensor {entity} wurde nicht gefunden. Prüfe die Card-Konfiguration und die ChoreFlow-Integration.","count.open":"{count} offen","tab.tasks":"Aufgaben","tab.history":"Verlauf","action.create":"Aufgabe erstellen","action.complete":"Erledigen","action.edit":"Bearbeiten","action.snooze":"Später erinnern","action.correct":"Korrigieren","action.revert_completion":"Erledigung rückgängig machen","action.close":"Schließen","action.cancel":"Abbrechen","action.save":"Speichern","action.create_short":"Erstellen","action.retry":"Erneut versuchen","action.load_more":"Mehr laden","stat.open":"Offen","stat.due":"Fällig","stat.overdue":"Überfällig","stat.completed_today":"Heute erledigt","filter.all":"Alle","filter.room_aria":"Raum filtern","filter.all_rooms":"Alle Räume","filter.category_aria":"Kategorie filtern","filter.all_categories":"Alle Kategorien","filter.group_room":"Nach Raum","tasks.loading":"Aufgaben werden geladen …","tasks.refreshing":"Aufgaben werden aktualisiert …","tasks.preview_total":"Teilansicht: {shown} von {total} offenen Aufgaben werden aus der Sensor-Vorschau angezeigt.","tasks.preview_truncated":"Teilansicht: Die Sensor-Vorschau ist gekürzt; weitere offene Aufgaben sind derzeit nicht geladen.","tasks.empty":"Für diesen Filter ist nichts offen.","tasks.no_room":"Ohne Raum","urgency.overdue":"Überfällig · {count} {unit}","urgency.today_important":"Heute fällig · Wichtig","urgency.today":"Heute fällig","urgency.tomorrow_important":"Morgen fällig · Wichtig","urgency.soon_important":"Bald fällig · Wichtig","unit.day":"Tag","unit.days":"Tage","unit.minutes_short":"Min","task.snoozed_tomorrow":"Aufgeschoben bis morgen","task.completed":"Erledigt","history.title":"Verlauf","history.loading":"Lädt…","history.empty":"Noch keine Einträge.","history.completed":"Erledigt","history.completed_todo":"Erledigt (To-do)","history.corrected":"Korrigiert","history.snoozed":"Später erinnert","history.created":"Erstellt","history.updated":"Geändert","history.deleted":"Gelöscht","history.notified":"Benachrichtigt","history.missed":"Verpasst (abwesend)","history.expired":"Abgelaufen","history.from_todo":"Aus To-do","history.calendar_created":"Kalender erstellt","history.calendar_removed":"Kalender entfernt","person.who":"Wer bist du?","person.none":"Keine Personen gefunden. Bitte persons oder default_person in der Kartenkonfiguration setzen.","edit.title":"Aufgabe bearbeiten","field.title":"Titel","field.description":"Beschreibung","field.room":"Raum","field.category":"Kategorie","field.importance":"Wichtigkeit","field.duration":"Dauer (Min)","field.due_date":"Fälligkeitsdatum","field.person":"Person","importance.high":"Hoch","importance.normal":"Normal","importance.low":"Niedrig","recurrence.title":"Wiederholung","recurrence.once":"Einmalig","recurrence.every_n_days":"Alle N Tage","recurrence.weekdays":"Wochentage","recurrence.interval":"Intervall (Tage)","weekday.mon":"Mo","weekday.tue":"Di","weekday.wed":"Mi","weekday.thu":"Do","weekday.fri":"Fr","weekday.sat":"Sa","weekday.sun":"So","create.title":"Neue Aufgabe","create.title_placeholder":"z. B. Bad putzen","create.room_placeholder":"Küche","create.category_placeholder":"Reinigung","create.due":"Fällig am","create.visibility_assignment":"Sichtbarkeit & Zuweisung","create.visible_to":"Sichtbar für","create.all_persons":"Alle Personen","create.selected":"Ausgewählte","create.assignment":"Zuweisung","create.random":"Zufällig","create.fixed_person":"Feste Person","create.choose_person":"Person wählen…","create.calendar_export":"Kalender-Export","create.calendar_entity":"Kalender-Entität (optional)","create.calendar_help":"Falls angegeben, wird der Fälligkeitstermin als Termin im gewählten Kalender angelegt.","editor.global_sensors":"Globale Sensoren","editor.open_required":"Offene Aufgaben (Pflicht)","editor.due":"Fällige Aufgaben","editor.overdue":"Überfällige Aufgaben","editor.completed_today":"Heute erledigt","editor.completed_week":"Diese Woche erledigt","editor.active_chains":"Aktive Ketten","editor.persons":"Personen","editor.remove":"Entfernen","editor.open":"Offen","editor.remaining_today":"Verbleibend heute","editor.has_due":"Hat fällige Aufgaben","editor.chain_active":"Kette aktiv","editor.add_person":"+ Person hinzufügen","editor.options":"Optionen","editor.show_create":"Erstellen-Dialog anzeigen","editor.show_history":"Verlauf-Tab anzeigen","editor.default_person":"Standard-Person"},en:{"task.load_error":"Tasks could not be loaded.","due.none":"No due date","date.yesterday":"Yesterday","date.days_ago":"{count} days ago","date.today":"Today","date.tomorrow":"Tomorrow","date.today_time":"Today {time}","date.yesterday_time":"Yesterday {time}","edit.duration_error":"Duration must be a whole number between 1 and 1440 minutes.","error.not_visible":"This task is not visible to you.","error.not_assigned":"This task is not assigned to you.","error.not_open":"This task is no longer open.","error.person_disabled":"This person is not enabled.","error.action_failed":"Action failed.","card.unavailable":"ChoreFlow unavailable","card.sensor_missing":"The required sensor {entity} was not found. Check the card configuration and the ChoreFlow integration.","count.open":"{count} open","tab.tasks":"Tasks","tab.history":"History","action.create":"Create task","action.complete":"Complete","action.edit":"Edit","action.snooze":"Remind later","action.correct":"Correct","action.revert_completion":"Undo completion","action.close":"Close","action.cancel":"Cancel","action.save":"Save","action.create_short":"Create","action.retry":"Try again","action.load_more":"Load more","stat.open":"Open","stat.due":"Due","stat.overdue":"Overdue","stat.completed_today":"Completed today","filter.all":"All","filter.room_aria":"Filter by room","filter.all_rooms":"All rooms","filter.category_aria":"Filter by category","filter.all_categories":"All categories","filter.group_room":"By room","tasks.loading":"Loading tasks …","tasks.refreshing":"Updating tasks …","tasks.preview_total":"Partial view: {shown} of {total} open tasks are shown from the sensor preview.","tasks.preview_truncated":"Partial view: The sensor preview is truncated; more open tasks are not currently loaded.","tasks.empty":"Nothing is open for this filter.","tasks.no_room":"No room","urgency.overdue":"Overdue · {count} {unit}","urgency.today_important":"Due today · Important","urgency.today":"Due today","urgency.tomorrow_important":"Due tomorrow · Important","urgency.soon_important":"Due soon · Important","unit.day":"day","unit.days":"days","unit.minutes_short":"min","task.snoozed_tomorrow":"Snoozed until tomorrow","task.completed":"Completed","history.title":"History","history.loading":"Loading…","history.empty":"No entries yet.","history.completed":"Completed","history.completed_todo":"Completed (to-do)","history.corrected":"Corrected","history.snoozed":"Reminded later","history.created":"Created","history.updated":"Updated","history.deleted":"Deleted","history.notified":"Notified","history.missed":"Missed (away)","history.expired":"Expired","history.from_todo":"From to-do","history.calendar_created":"Calendar created","history.calendar_removed":"Calendar removed","person.who":"Who are you?","person.none":"No persons found. Set persons or default_person in the card configuration.","edit.title":"Edit task","field.title":"Title","field.description":"Description","field.room":"Room","field.category":"Category","field.importance":"Importance","field.duration":"Duration (min)","field.due_date":"Due date","field.person":"Person","importance.high":"High","importance.normal":"Normal","importance.low":"Low","recurrence.title":"Recurrence","recurrence.once":"Once","recurrence.every_n_days":"Every N days","recurrence.weekdays":"Weekdays","recurrence.interval":"Interval (days)","weekday.mon":"Mon","weekday.tue":"Tue","weekday.wed":"Wed","weekday.thu":"Thu","weekday.fri":"Fri","weekday.sat":"Sat","weekday.sun":"Sun","create.title":"New task","create.title_placeholder":"e.g. clean bathroom","create.room_placeholder":"Kitchen","create.category_placeholder":"Cleaning","create.due":"Due on","create.visibility_assignment":"Visibility & assignment","create.visible_to":"Visible to","create.all_persons":"All persons","create.selected":"Selected","create.assignment":"Assignment","create.random":"Random","create.fixed_person":"Specific person","create.choose_person":"Choose person…","create.calendar_export":"Calendar export","create.calendar_entity":"Calendar entity (optional)","create.calendar_help":"When provided, the due date is created as an event in the selected calendar.","editor.global_sensors":"Global sensors","editor.open_required":"Open tasks (required)","editor.due":"Due tasks","editor.overdue":"Overdue tasks","editor.completed_today":"Completed today","editor.completed_week":"Completed this week","editor.active_chains":"Active chains","editor.persons":"Persons","editor.remove":"Remove","editor.open":"Open","editor.remaining_today":"Remaining today","editor.has_due":"Has due tasks","editor.chain_active":"Chain active","editor.add_person":"+ Add person","editor.options":"Options","editor.show_create":"Show create dialog","editor.show_history":"Show history tab","editor.default_person":"Default person"}};function ft(t){return t?.locale?.language??t?.language??"en"}function vt(t,e,i={}){let o=yt[function(t){return(t?.locale?.language??t?.language??"en").toLowerCase().startsWith("de")?"de":"en"}(t)][e];for(const[t,e]of Object.entries(i))o=o.replaceAll(`{${t}}`,String(e));return o}let bt=class extends at{_t(t){return vt(this.hass,t)}setConfig(t){this._config={...t,entities:{...t.entities,open_tasks:t.entities?.open_tasks??""}}}_emit(t){this._config=t,this.dispatchEvent(new CustomEvent("config-changed",{detail:{config:t},bubbles:!0,composed:!0}))}_setGlobal(t,e){this._emit({...this._config,entities:{...this._config.entities,[t]:e}})}_setRoot(t,e){this._emit({...this._config,[t]:e})}_setPerson(t,e){const i=[...this._config.persons??[]];i[t]={...i[t],...e},this._emit({...this._config,persons:i})}_addPerson(){this._emit({...this._config,persons:[...this._config.persons??[],{entity:""}]})}_removePerson(t){const e=[...this._config.persons??[]];e.splice(t,1),this._emit({...this._config,persons:e})}_sensorPicker(t,e,i,o=["sensor"]){return customElements.get("ha-entity-picker")?B`<ha-entity-picker
        .hass=${this.hass}
        .label=${t}
        .value=${e??""}
        .includeDomains=${o}
        allow-custom-entity
        @value-changed=${t=>i(t.detail.value)}
      ></ha-entity-picker>`:B`<label class="row"><span>${t}</span><input .value=${e??""} @input=${t=>i(t.target.value)} /></label>`}render(){if(!this._config||!this.hass)return B``;const t=this._config.entities;return B`
      <div class="form">
        <label class="row"><span>${this._t("field.title")}</span><input .value=${this._config.title??""} @input=${t=>this._setRoot("title",t.target.value)} /></label>

        <h4>${this._t("editor.global_sensors")}</h4>
        ${this._sensorPicker(this._t("editor.open_required"),t.open_tasks,t=>this._setGlobal("open_tasks",t))}
        ${this._sensorPicker(this._t("editor.due"),t.due_tasks,t=>this._setGlobal("due_tasks",t))}
        ${this._sensorPicker(this._t("editor.overdue"),t.overdue_tasks,t=>this._setGlobal("overdue_tasks",t))}
        ${this._sensorPicker(this._t("editor.completed_today"),t.completed_today,t=>this._setGlobal("completed_today",t))}
        ${this._sensorPicker(this._t("editor.completed_week"),t.completed_this_week,t=>this._setGlobal("completed_this_week",t))}
        ${this._sensorPicker(this._t("editor.active_chains"),t.active_chains,t=>this._setGlobal("active_chains",t))}

        <h4>${this._t("editor.persons")}</h4>
        ${(this._config.persons??[]).map((t,e)=>B`
            <div class="person">
              <div class="person-head">
                ${this._sensorPicker(this._t("field.person"),t.entity,t=>this._setPerson(e,{entity:t}),["person"])}
                <button class="del" @click=${()=>this._removePerson(e)} title=${this._t("editor.remove")}>✕</button>
              </div>
              ${this._sensorPicker(this._t("editor.open"),t.open_tasks,t=>this._setPerson(e,{open_tasks:t}))}
              ${this._sensorPicker(this._t("stat.due"),t.due_tasks,t=>this._setPerson(e,{due_tasks:t}))}
              ${this._sensorPicker(this._t("editor.completed_today"),t.completed_today,t=>this._setPerson(e,{completed_today:t}))}
              ${this._sensorPicker(this._t("editor.remaining_today"),t.remaining_today,t=>this._setPerson(e,{remaining_today:t}))}
              ${this._sensorPicker(this._t("editor.has_due"),t.has_due_tasks,t=>this._setPerson(e,{has_due_tasks:t}),["binary_sensor"])}
              ${this._sensorPicker(this._t("editor.chain_active"),t.chain_active,t=>this._setPerson(e,{chain_active:t}),["binary_sensor"])}
            </div>`)}
        <button class="add" @click=${this._addPerson}>${this._t("editor.add_person")}</button>

        <h4>${this._t("editor.options")}</h4>
        <label class="check"><input type="checkbox" .checked=${!1!==this._config.show_create} @change=${t=>this._setRoot("show_create",t.target.checked)} />${this._t("editor.show_create")}</label>
        <label class="check"><input type="checkbox" .checked=${!1!==this._config.show_history} @change=${t=>this._setRoot("show_history",t.target.checked)} />${this._t("editor.show_history")}</label>
        ${this._sensorPicker(this._t("editor.default_person"),this._config.default_person,t=>this._setRoot("default_person",t),["person"])}
      </div>
    `}};bt.styles=n`
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
  `,t([pt({attribute:!1})],bt.prototype,"hass",void 0),t([_t()],bt.prototype,"_config",void 0),bt=t([dt("choreflow-card-editor")],bt);let kt=class extends at{constructor(){super(...arguments),this._tab="tasks",this._personFilter="all",this._roomFilter="all",this._categoryFilter="all",this._groupByRoom=!1,this._dialogOpen=!1,this._personPickerOpen=!1,this._pendingAction=null,this._rowState={},this._rowError={},this._tasks=null,this._tasksLoading=!1,this._showTaskRefresh=!1,this._tasksError=null,this._taskRequestGeneration=0,this._taskConfigResetPending=!1,this._editForm=null,this._editSaving=!1,this._editError=null,this._history=[],this._historyTotal=0,this._historyLoading=!1,this._historyOffset=0}_t(t,e={}){return vt(this.hass,t,e)}static getConfigElement(){return document.createElement("choreflow-card-editor")}static getStubConfig(){return{title:"ChoreFlow",entities:{open_tasks:"sensor.choreflow_open_tasks",due_tasks:"sensor.choreflow_due_tasks",overdue_tasks:"sensor.choreflow_overdue_tasks",completed_today:"sensor.choreflow_completed_today",completed_this_week:"sensor.choreflow_completed_this_week",active_chains:"sensor.choreflow_active_chains"},persons:[],show_create:!0,show_history:!0}}setConfig(t){if(!t||!t.entities||!t.entities.open_tasks)throw new Error("choreflow-card: 'entities.open_tasks' is required (for example sensor.choreflow_open_tasks).");const e=this._config,i={show_create:!0,show_history:!0,...t,persons:t.persons??[]},o=i.default_person??"all",r=i.default_room??"all",s=!e||e.entities.open_tasks!==i.entities.open_tasks,n=!e||(e.default_person??"all")!==o,a=!e||(e.default_room??"all")!==r;this._config=i;let l=n;n?this._personFilter=o:"all"===this._personFilter||this._personFilter===o||i.persons.some(t=>t.entity===this._personFilter)||(this._personFilter=o,l=!0),a&&(this._roomFilter=r),e||(this._categoryFilter="all"),(s||l)&&(this._tasks=null,this._tasksError=null,this._taskRequestGeneration+=1,this._taskConfigResetPending=!0)}getCardSize(){return 6}updated(t){const e=t.get("hass"),i=t.get("_config"),o=i?.entities.open_tasks??this._config?.entities.open_tasks,r=this._taskConfigResetPending;this._taskConfigResetPending=!1;const s=t.has("hass")&&(o?e?.states[o]:void 0)!==this._openSensor;this.hass&&this._config&&(r||s)&&this._loadTasks(r||null===this._tasks),"history"===this._tab&&this._config?.show_history&&0===this._history.length&&!this._historyLoading&&0===this._historyOffset&&this._loadHistory(!0)}get _openSensor(){const t=this._config?.entities.open_tasks;return t?this.hass?.states[t]:void 0}_openTasks(){const t=this._openSensor?.attributes?.open_tasks;return Array.isArray(t)?t:[]}_baseTasks(){return null!==this._tasks?this._tasks:"all"===this._personFilter?this._openTasks():[]}_truncatedPreview(){if(null!==this._tasks||"all"!==this._personFilter)return null;const t=this._openSensor?.attributes,e=this._openTasks().length,i=Number(t?.total),o=Number.isFinite(i)?i:null;return!0===t?.truncated||"true"===t?.truncated||null!==o&&o>e?{shown:e,total:o}:null}async _setPersonFilter(t){t===this._personFilter&&null!==this._tasks||(this._personFilter=t,this._roomFilter="all",this._categoryFilter="all",this._tasks=null,this._tasksError=null,await this._loadTasks(!0))}_retryTasks(){this._loadTasks(null===this._tasks)}async _loadTasks(t){const e=++this._taskRequestGeneration,i=t?null:this._tasks;t&&(this._tasks=null),this._tasksLoading=!0,this._showTaskRefresh=!1,void 0!==this._taskRefreshTimer&&(window.clearTimeout(this._taskRefreshTimer),this._taskRefreshTimer=void 0),t?this._tasksError=null:this._taskRefreshTimer=window.setTimeout(()=>{e===this._taskRequestGeneration&&this._tasksLoading&&(this._showTaskRefresh=!0)},300);const o="all"===this._personFilter?void 0:this._personFilter,r=[];let s=0;try{for(;;){const t={status:"open",person_scope:"visible",limit:100,offset:s};o&&(t.person_entity=o);const e=await this.hass.connection.sendMessagePromise({type:"call_service",domain:"choreflow",service:"get_tasks",service_data:t,return_response:!0}),i=this._validateTaskPage(e?.response);if(r.push(...i.items),!i.has_more)break;if(0===i.received)throw new Error("get_tasks returned an empty page with has_more=true");s+=i.received}if(e!==this._taskRequestGeneration)return;this._tasks=r,this._tasksError=null}catch(t){if(e!==this._taskRequestGeneration)return;console.error("[choreflow] get_tasks",t),this._tasks=i,this._tasksError=this._t("task.load_error")}finally{e===this._taskRequestGeneration&&(void 0!==this._taskRefreshTimer&&(window.clearTimeout(this._taskRefreshTimer),this._taskRefreshTimer=void 0),this._tasksLoading=!1,this._showTaskRefresh=!1)}}_validateTaskPage(t){if(!t||"object"!=typeof t)throw new Error("Invalid get_tasks response");const e=t;if(!Array.isArray(e.items)||"boolean"!=typeof e.has_more)throw new Error("Invalid get_tasks page");const i=e.items.filter(t=>this._isTask(t)),o=e.items.length-i.length;return o>0&&console.warn(`[choreflow] get_tasks dropped ${o} invalid task item(s)`),{items:i,has_more:e.has_more,received:e.items.length}}_isTask(t){if(!t||"object"!=typeof t)return!1;const e=t;return!("string"!=typeof e.task_id||"string"!=typeof e.title||"string"!=typeof e.room||"string"!=typeof e.category||"low"!==e.importance&&"normal"!==e.importance&&"high"!==e.importance||null!=e.estimated_duration_minutes&&"number"!=typeof e.estimated_duration_minutes||null!=e.due_date&&"string"!=typeof e.due_date||null!=e.snooze_until&&"string"!=typeof e.snooze_until)}_num(t){if(!t)return null;const e=this.hass?.states[t];if(!e||"unknown"===e.state||"unavailable"===e.state)return null;const i=Number(e.state);return Number.isFinite(i)?i:null}_personName(t){const e=this.hass?.states[t.entity];return e?.attributes?.friendly_name||t.entity.split(".").pop()||t.entity}_dueInfo(t){if(!t)return{label:this._t("due.none"),overdueDays:0,isOverdue:!1,isToday:!1,rank:100};const e=new Date;e.setHours(0,0,0,0);const i=new Date(t+"T00:00:00"),o=Math.round((i.getTime()-e.getTime())/864e5);if(o<0){const t=-o;return{label:1===t?this._t("date.yesterday"):this._t("date.days_ago",{count:t}),overdueDays:t,isOverdue:!0,isToday:!1,rank:1e3+t}}return 0===o?{label:this._t("date.today"),overdueDays:0,isOverdue:!1,isToday:!0,rank:600}:1===o?{label:this._t("date.tomorrow"),overdueDays:0,isOverdue:!1,isToday:!1,rank:300}:{label:i.toLocaleDateString(ft(this.hass),{weekday:"short",day:"2-digit",month:"2-digit"}),overdueDays:0,isOverdue:!1,isToday:!1,rank:200}}_relTime(t){const e=new Date(t),i=new Date,o=e.toDateString()===i.toDateString(),r=new Date(i);r.setDate(i.getDate()-1);const s=ft(this.hass),n=e.toLocaleTimeString(s,{hour:"2-digit",minute:"2-digit"});return o?this._t("date.today_time",{time:n}):e.toDateString()===r.toDateString()?this._t("date.yesterday_time",{time:n}):e.toLocaleDateString(s,{weekday:"short",day:"2-digit",month:"2-digit"})}_defaultPerson(){return this._config.default_person??("all"!==this._personFilter?this._personFilter:void 0)??this._config.persons?.[0]?.entity}_availablePersonsForPicker(){return this._config.persons?.length?this._config.persons.map(t=>({entity:t.entity,name:this._personName(t)})):Object.keys(this.hass.states).filter(t=>t.startsWith("person.")).map(t=>({entity:t,name:this.hass.states[t].attributes?.friendly_name||t.split(".").pop()||t}))}async _completeTask(t){if("pending"===this._rowState[t]||"done"===this._rowState[t])return;const e=this._defaultPerson();if(!e)return this._pendingAction={taskId:t,action:"complete"},void(this._personPickerOpen=!0);await this._executeComplete(t,e)}async _executeComplete(t,e){this._setRow(t,"pending"),this._clearRowError(t);try{await this.hass.callService("choreflow","complete_task",{task_id:t,person_entity:e,source:"dashboard"}),this._setRow(t,"done")}catch(e){this._setRow(t,"idle"),this._setRowError(t,this._friendlyError(e))}}async _snoozeTask(t){if("pending"===this._rowState[t]||"snoozed"===this._rowState[t])return;const e=this._defaultPerson();if(!e)return this._pendingAction={taskId:t,action:"snooze"},void(this._personPickerOpen=!0);await this._executeSnooze(t,e)}async _executeSnooze(t,e){this._setRow(t,"pending"),this._clearRowError(t);try{await this.hass.callService("choreflow","snooze_task",{task_id:t,person_entity:e}),this._setRow(t,"snoozed")}catch(e){this._setRow(t,"idle"),this._setRowError(t,this._friendlyError(e))}}async _reopenTask(t){try{await this.hass.callService("choreflow","reopen_task",{task_id:t}),await this._loadHistory(!0)}catch(t){console.error("[choreflow] reopen_task",t)}}async _openEdit(t){const e=await this.hass.connection.sendMessagePromise({type:"call_service",domain:"choreflow",service:"get_task",service_data:{task_id:t},return_response:!0}),i=e?.response;i&&(this._editError=null,this._editForm={task_id:t,task_rule_id:i.task_rule_id??null,title:i.title??"",description:i.description??"",room:i.room??"",category:i.category??"",importance:i.importance??"normal",due_date:i.due_date??"",estimated_duration_minutes:null!=i.estimated_duration_minutes?String(i.estimated_duration_minutes):"",recurrence_type:i.recurrence_type??"once",recurrence_interval:null!=i.recurrence_interval?String(i.recurrence_interval):"1",recurrence_weekdays:i.recurrence_weekdays??[]})}_closeEdit(){this._editForm=null,this._editSaving=!1,this._editError=null}_setEditField(t,e){this._editForm&&(this._editForm={...this._editForm,[t]:e},this._editError=null)}_toggleEditWeekday(t){if(!this._editForm)return;const e=this._editForm.recurrence_weekdays,i=e.includes(t)?e.filter(e=>e!==t):[...e,t];this._editForm={...this._editForm,recurrence_weekdays:i},this._editError=null}async _saveEdit(){if(!this._editForm||this._editSaving)return;const t=this._editForm,e=t.estimated_duration_minutes.trim(),i=e?Number(e):null;if(null!==i&&(!Number.isInteger(i)||i<1||i>1440))return void(this._editError=this._t("edit.duration_error"));this._editSaving=!0,this._editError=null;const o={task_id:t.task_id,title:t.title,description:t.description.trim()||null,room:t.room||void 0,category:t.category||void 0,importance:t.importance,due_date:t.due_date||null,estimated_duration_minutes:i};t.task_rule_id&&(o.recurrence_type=t.recurrence_type,"every_n_days"===t.recurrence_type?o.recurrence_interval=Number(t.recurrence_interval)||1:"weekdays"===t.recurrence_type&&(o.recurrence_weekdays=t.recurrence_weekdays));try{await this.hass.callService("choreflow","update_task",o),this._closeEdit()}catch(t){console.error("[choreflow] update_task",t),this._editError=this._friendlyError(t),this._editSaving=!1}}async _createTask(t){const e=await this.hass.connection.sendMessagePromise({type:"call_service",domain:"choreflow",service:"create_task",service_data:t,return_response:!0});return e?.response??{}}async _loadHistory(t=!1){if(!this._config.show_history)return;this._historyLoading=!0;const e=t?0:this._historyOffset;try{const i=await this.hass.connection.sendMessagePromise({type:"call_service",domain:"choreflow",service:"get_history",service_data:{limit:10,offset:e},return_response:!0}),o=i?.response;o&&(this._history=t?o.items:[...this._history,...o.items],this._historyTotal=o.total,this._historyOffset=e+o.items.length)}catch(t){console.error("[choreflow] get_history",t)}finally{this._historyLoading=!1}}_friendlyError(t){const e=t?.message??"";return/visib|sicht/i.test(e)?this._t("error.not_visible"):/assign|zuweis/i.test(e)?this._t("error.not_assigned"):/not open|nicht offen|unknown|unbekannt/i.test(e)?this._t("error.not_open"):/person/i.test(e)?this._t("error.person_disabled"):this._t("error.action_failed")}_setRow(t,e){this._rowState={...this._rowState,[t]:e}}_setRowError(t,e){this._rowError={...this._rowError,[t]:e},window.setTimeout(()=>this._clearRowError(t),5e3)}_clearRowError(t){if(!this._rowError[t])return;const e={...this._rowError};delete e[t],this._rowError=e}_localDate(t=new Date){return`${t.getFullYear()}-${String(t.getMonth()+1).padStart(2,"0")}-${String(t.getDate()).padStart(2,"0")}`}_isSnoozed(t){const e=this._localDate();return"snoozed"===this._rowState[t.task_id]||!!t.snooze_until&&t.snooze_until>e}_visibleTasks(){let t=this._baseTasks().filter(t=>"done"!==this._rowState[t.task_id]);return"all"!==this._roomFilter&&(t=t.filter(t=>t.room===this._roomFilter)),"all"!==this._categoryFilter&&(t=t.filter(t=>t.category===this._categoryFilter)),t.slice().sort((t,e)=>{const i=this._isSnoozed(t);return i!==this._isSnoozed(e)?i?1:-1:this._dueInfo(e.due_date).rank+$t(e.importance)-(this._dueInfo(t.due_date).rank+$t(t.importance))})}_rooms(){return[...new Set(this._baseTasks().map(t=>t.room).filter(Boolean))]}_categories(){return[...new Set(this._baseTasks().map(t=>t.category).filter(Boolean))]}render(){if(!this._config||!this.hass)return B``;if(!this._openSensor)return B`<ha-card>
        <div class="error">
          <ha-icon icon="mdi:alert"></ha-icon>
          <div>
            <div class="error-title">${this._t("card.unavailable")}</div>
            <div class="error-body">
              ${this._t("card.sensor_missing",{entity:this._config.entities.open_tasks})}
            </div>
          </div>
        </div>
      </ha-card>`;const t=this._num(this._config.entities.open_tasks)??this._openTasks().length,e=this._num(this._config.entities.due_tasks),i=this._num(this._config.entities.overdue_tasks),o=this._num(this._config.entities.completed_today);return B`
      <ha-card>
        <div class="head">
          <div class="title">
            <span class="title-text">${this._config.title??"ChoreFlow"}</span>
            <span class="sub">${this._t("count.open",{count:t})}</span>
          </div>
          <div class="head-actions">
            ${this._config.show_history?B`<div class="seg" role="tablist">
                  <button role="tab" class=${mt({on:"tasks"===this._tab})} @click=${()=>this._tab="tasks"}>${this._t("tab.tasks")}</button>
                  <button role="tab" class=${mt({on:"history"===this._tab})} @click=${()=>this._tab="history"}>${this._t("tab.history")}</button>
                </div>`:q}
            ${this._config.show_create?B`<button class="icon-btn primary" aria-label=${this._t("action.create")} title=${this._t("action.create")} @click=${()=>this._dialogOpen=!0}>
                  <ha-icon icon="mdi:plus"></ha-icon>
                </button>`:q}
          </div>
        </div>

        <div class="stats">
          ${this._stat(t,this._t("stat.open"))} ${this._stat(e,this._t("stat.due"))}
          ${this._stat(i,this._t("stat.overdue"),i&&i>0?"error":"")}
          ${this._stat(o,this._t("stat.completed_today"))}
        </div>

        ${"tasks"===this._tab?this._renderTasks():this._renderHistory()}
      </ha-card>

      ${this._dialogOpen?this._renderDialog():q}
      ${this._personPickerOpen?this._renderPersonPicker():q}
      ${this._editForm?this._renderEditDialog():q}
    `}_stat(t,e,i=""){return B`<div class="stat">
      <div class="stat-num ${i}">${t??"—"}</div>
      <div class="stat-label">${e}</div>
    </div>`}_renderTasks(){const t=this._visibleTasks(),e=this._rooms(),i=this._categories(),o=this._truncatedPreview();return B`
      <div class="filters">
        <div class="seg">
          <button class=${mt({on:"all"===this._personFilter})} @click=${()=>{this._setPersonFilter("all")}}>${this._t("filter.all")}</button>
          ${(this._config.persons??[]).map(t=>B`<button class=${mt({on:this._personFilter===t.entity})} @click=${()=>{this._setPersonFilter(t.entity)}}>${this._personName(t)}</button>`)}
        </div>
        <select aria-label=${this._t("filter.room_aria")} .value=${this._roomFilter} @change=${t=>this._roomFilter=t.target.value}>
          <option value="all">${this._t("filter.all_rooms")}</option>
          ${e.map(t=>B`<option value=${t}>${t}</option>`)}
        </select>
        <select aria-label=${this._t("filter.category_aria")} .value=${this._categoryFilter} @change=${t=>this._categoryFilter=t.target.value}>
          <option value="all">${this._t("filter.all_categories")}</option>
          ${i.map(t=>B`<option value=${t}>${t}</option>`)}
        </select>
        <button class=${mt({chiptoggle:!0,on:this._groupByRoom})} @click=${()=>this._groupByRoom=!this._groupByRoom}>
          <ha-icon icon="mdi:view-list"></ha-icon>${this._t("filter.group_room")}
        </button>
      </div>

      ${this._tasksLoading&&null===this._tasks?B`<div class="task-status"><span class="spin"><ha-icon icon="mdi:loading"></ha-icon></span>${this._t("tasks.loading")}</div>`:this._showTaskRefresh?B`<div class="task-status"><span class="spin"><ha-icon icon="mdi:loading"></ha-icon></span>${this._t("tasks.refreshing")}</div>`:q}
      ${this._tasksError?B`<div class="task-status task-error">
            <ha-icon icon="mdi:alert-outline"></ha-icon>
            <span>${this._tasksError}</span>
            <button type="button" @click=${()=>this._retryTasks()}>${this._t("action.retry")}</button>
          </div>`:q}
      ${o?B`<div class="preview-hint">
            <ha-icon icon="mdi:information-outline"></ha-icon>
            <span>
              ${null!==o.total?this._t("tasks.preview_total",{shown:o.shown,total:o.total}):this._t("tasks.preview_truncated")}
            </span>
          </div>`:q}

      ${0===t.length&&null===this._tasks&&(this._tasksLoading||this._tasksError)?q:0===t.length?B`<div class="empty"><ha-icon icon="mdi:check"></ha-icon><p>${this._t("tasks.empty")}</p></div>`:this._groupByRoom?this._groupTasks(t):B`<div class="list">${t.map(t=>this._renderRow(t))}</div>`}
    `}_groupTasks(t){const e=new Map;for(const i of t){const t=i.room||this._t("tasks.no_room");e.has(t)||e.set(t,[]),e.get(t).push(i)}return B`<div class="list">
      ${[...e.entries()].map(([t,e])=>B`
          <div class="group-head"><ha-icon icon="mdi:map-marker"></ha-icon>${t}<span class="group-count">· ${e.length}</span></div>
          ${e.map(t=>this._renderRow(t))}
        `)}
    </div>`}_renderRow(t){const e=this._dueInfo(t.due_date),i=t.due_date?Math.round((new Date(t.due_date+"T00:00:00").getTime()-(new Date).setHours(0,0,0,0))/864e5):null;let o="normal";e.isOverdue?o="overdue":"high"===t.importance?o="high":e.isToday&&(o="today");let r="",s="";e.isOverdue?(r="mdi:alert",s=this._t("urgency.overdue",{count:e.overdueDays,unit:this._t(1===e.overdueDays?"unit.day":"unit.days")})):e.isToday&&"high"===t.importance?(r="mdi:alert-circle",s=this._t("urgency.today_important")):e.isToday?(r="mdi:clock-outline",s=this._t("urgency.today")):"high"===t.importance&&null!==i&&i<=2&&(r="mdi:chevron-up",s=1===i?this._t("urgency.tomorrow_important"):this._t("urgency.soon_important"));const n=this._rowState[t.task_id]??"idle",a=this._isSnoozed(t),l=this._rowError[t.task_id],d=!!t.task_id,c=[t.room,t.category];return t.estimated_duration_minutes&&c.push(`${t.estimated_duration_minutes} ${this._t("unit.minutes_short")}`),B`<div class=${mt({row:!0,[o]:!0,settled:"done"===n,"row-snoozed":a})}>
      <div class="row-main">
        <div class="row-top">
          <span class="row-title ${"done"===n?"struck":""}">${t.title}</span>
          <span class="due ${o}">${e.label}</span>
        </div>
        <div class="row-meta">
          ${s?B`<span class="urg ${o}"><ha-icon icon=${r}></ha-icon>${s}</span>`:q}
          <span class="meta-text">${s?"· ":""}${c.join(" · ")}</span>
        </div>
        ${a?B`<div class="snooze-badge"><ha-icon icon="mdi:clock-outline"></ha-icon>${this._t("task.snoozed_tomorrow")}</div>`:q}
        ${l?B`<div class="row-error"><ha-icon icon="mdi:alert"></ha-icon>${l}</div>`:q}
      </div>
      <div class="row-actions">
        ${"pending"===n?B`<span class="spin"><ha-icon icon="mdi:loading"></ha-icon></span>`:"done"===n?B`<span class="settle ok"><ha-icon icon="mdi:check-circle"></ha-icon>${this._t("task.completed")}</span>`:a?B`
              <button class="icon-btn ok" aria-label=${this._t("action.complete")} title=${this._t("action.complete")} @click=${()=>this._completeTask(t.task_id)}>
                <ha-icon icon="mdi:check-circle"></ha-icon>
              </button>
            `:d?B`
              <button class="icon-btn" aria-label=${this._t("action.edit")} title=${this._t("action.edit")} @click=${()=>this._openEdit(t.task_id)}>
                <ha-icon icon="mdi:pencil"></ha-icon>
              </button>
              <button class="icon-btn" aria-label=${this._t("action.snooze")} title=${this._t("action.snooze")} @click=${()=>this._snoozeTask(t.task_id)}>
                <ha-icon icon="mdi:clock-outline"></ha-icon>
              </button>
              <button class="icon-btn ok" aria-label=${this._t("action.complete")} title=${this._t("action.complete")} @click=${()=>this._completeTask(t.task_id)}>
                <ha-icon icon="mdi:check-circle"></ha-icon>
              </button>
            `:q}
      </div>
    </div>`}_renderHistory(){return B`
      <div class="hist-head">${this._t("history.title")}</div>
      ${0===this._history.length&&this._historyLoading?B`<div class="empty"><p>${this._t("history.loading")}</p></div>`:0===this._history.length?B`<div class="empty"><p>${this._t("history.empty")}</p></div>`:B`<div class="list">
            ${this._history.map(t=>{const e=function(t,e){switch(e){case"task_completed":return{icon:"mdi:check-circle",tone:"ok",label:vt(t,"history.completed")};case"task_completed_from_todo":return{icon:"mdi:clipboard-check",tone:"ok",label:vt(t,"history.completed_todo")};case"task_reopened":return{icon:"mdi:undo",tone:"warn",label:vt(t,"history.corrected")};case"task_snoozed":return{icon:"mdi:clock-outline",tone:"warn",label:vt(t,"history.snoozed")};case"task_created":return{icon:"mdi:plus-circle-outline",tone:"muted",label:vt(t,"history.created")};case"task_updated":return{icon:"mdi:pencil",tone:"muted",label:vt(t,"history.updated")};case"task_deleted":return{icon:"mdi:delete-outline",tone:"muted",label:vt(t,"history.deleted")};case"task_notified":return{icon:"mdi:bell-outline",tone:"muted",label:vt(t,"history.notified")};case"task_missed_no_presence":return{icon:"mdi:account-off-outline",tone:"err",label:vt(t,"history.missed")};case"task_expired":return{icon:"mdi:close-circle-outline",tone:"err",label:vt(t,"history.expired")};case"task_synced_from_todo":return{icon:"mdi:sync",tone:"muted",label:vt(t,"history.from_todo")};case"calendar_task_created":return{icon:"mdi:calendar-plus",tone:"muted",label:vt(t,"history.calendar_created")};case"calendar_task_removed":return{icon:"mdi:calendar-remove",tone:"muted",label:vt(t,"history.calendar_removed")};default:return{icon:"mdi:information-outline",tone:"muted",label:e}}}(this.hass,t.event_type),i=("task_completed"===t.event_type||"task_completed_from_todo"===t.event_type)&&!!t.task_id,o=[e.label,t.room,t.person_entity?xt(this.hass,t.person_entity):null].filter(Boolean);return B`<div class="hist">
                <ha-icon class=${e.tone} icon=${e.icon}></ha-icon>
                <div class="hist-main">
                  <div class="hist-top">
                    <span class="hist-title">${t.title??"—"}</span>
                    <span class="hist-time">${this._relTime(t.timestamp)}</span>
                  </div>
                  <div class="hist-meta">${o.join(" · ")}</div>
                </div>
                ${i?B`<button class="icon-btn" aria-label=${this._t("action.correct")} title=${this._t("action.revert_completion")} @click=${()=>this._reopenTask(t.task_id)}>
                      <ha-icon icon="mdi:undo"></ha-icon>
                    </button>`:q}
              </div>`})}
          </div>`}
      ${this._historyOffset<this._historyTotal?B`<button class="loadmore" ?disabled=${this._historyLoading} @click=${()=>this._loadHistory(!1)}>
             ${this._historyLoading?this._t("history.loading"):this._t("action.load_more")}
          </button>`:q}
    `}_renderPersonPicker(){const t=this._availablePersonsForPicker(),e=()=>{this._personPickerOpen=!1,this._pendingAction=null},i=async t=>{this._personPickerOpen=!1;const e=this._pendingAction;this._pendingAction=null,e&&("complete"===e.action?await this._executeComplete(e.taskId,t):await this._executeSnooze(e.taskId,t))};return B`<div class="overlay" @click=${e}>
      <div class="dialog" style="max-width:320px" @click=${t=>t.stopPropagation()}>
        <div class="dlg-head">
          <span>${this._t("person.who")}</span>
          <button type="button" class="icon-btn" aria-label=${this._t("action.close")} @click=${e}><ha-icon icon="mdi:close"></ha-icon></button>
        </div>
        <div class="dlg-body">
          ${t.length?t.map(t=>B`<button class="person-pick-btn" @click=${()=>i(t.entity)}>${t.name}</button>`):B`<p style="margin:0;font-size:13px;color:var(--secondary-text-color)">${this._t("person.none")}</p>`}
        </div>
      </div>
    </div>`}_renderEditDialog(){const t=this._editForm,e=!!t.task_rule_id;return B`<div class="overlay" @click=${()=>this._closeEdit()}>
      <div class="dialog edit-dialog" @click=${t=>t.stopPropagation()}>
        <div class="dlg-head">
          <span>${this._t("edit.title")}</span>
          <button type="button" class="icon-btn" aria-label=${this._t("action.close")} @click=${()=>this._closeEdit()}>
            <ha-icon icon="mdi:close"></ha-icon>
          </button>
        </div>
        <div class="dlg-body edit-body">
          ${this._editError?B`<div class="edit-error" role="alert"><ha-icon icon="mdi:alert-outline"></ha-icon>${this._editError}</div>`:q}
          <label class="edit-label">${this._t("field.title")}
            <input class="edit-input" type="text" .value=${t.title}
              @input=${t=>this._setEditField("title",t.target.value)} />
          </label>
          <label class="edit-label">${this._t("field.description")}
            <textarea class="edit-input edit-textarea" rows="2"
              @input=${t=>this._setEditField("description",t.target.value)}
            >${t.description}</textarea>
          </label>
          <div class="edit-row2">
            <label class="edit-label">${this._t("field.room")}
              <input class="edit-input" type="text" .value=${t.room}
                @input=${t=>this._setEditField("room",t.target.value)} />
            </label>
            <label class="edit-label">${this._t("field.category")}
              <input class="edit-input" type="text" .value=${t.category}
                @input=${t=>this._setEditField("category",t.target.value)} />
            </label>
          </div>
          <div class="edit-row2">
            <label class="edit-label">${this._t("field.importance")}
              <select class="edit-input" .value=${t.importance}
                @change=${t=>this._setEditField("importance",t.target.value)}>
                <option value="high" ?selected=${"high"===t.importance}>${this._t("importance.high")}</option>
                <option value="normal" ?selected=${"normal"===t.importance}>${this._t("importance.normal")}</option>
                <option value="low" ?selected=${"low"===t.importance}>${this._t("importance.low")}</option>
              </select>
            </label>
            <label class="edit-label">${this._t("field.duration")}
              <input class="edit-input" type="number" min="1" max="1440" .value=${t.estimated_duration_minutes}
                @input=${t=>this._setEditField("estimated_duration_minutes",t.target.value)} />
            </label>
          </div>
          <label class="edit-label">${this._t("field.due_date")}
            <input class="edit-input" type="date" .value=${t.due_date}
              @change=${t=>this._setEditField("due_date",t.target.value)} />
          </label>
          ${e?B`
            <div class="edit-section-head">${this._t("recurrence.title")}</div>
            <div class="edit-recurrence-btns">
              ${["once","every_n_days","weekdays"].map(e=>B`
                <button class=${mt({"recurrence-btn":!0,active:t.recurrence_type===e})}
                  type="button" @click=${()=>this._setEditField("recurrence_type",e)}>
                  ${this._t(`recurrence.${e}`)}
                </button>`)}
            </div>
            ${"every_n_days"===t.recurrence_type?B`
              <label class="edit-label">${this._t("recurrence.interval")}
                <input class="edit-input" type="number" min="1" max="365" .value=${t.recurrence_interval}
                  @input=${t=>this._setEditField("recurrence_interval",t.target.value)} />
              </label>`:q}
            ${"weekdays"===t.recurrence_type?B`
              <div class="weekday-picker">
                ${["weekday.mon","weekday.tue","weekday.wed","weekday.thu","weekday.fri","weekday.sat","weekday.sun"].map((e,i)=>B`
                  <button type="button"
                    class=${mt({"wd-btn":!0,active:t.recurrence_weekdays.includes(i)})}
                    @click=${()=>this._toggleEditWeekday(i)}>${this._t(e)}</button>`)}
              </div>`:q}
          `:q}
        </div>
        <div class="dlg-footer">
          <button class="dlg-btn secondary" type="button" @click=${()=>this._closeEdit()}>${this._t("action.cancel")}</button>
          <button class="dlg-btn primary" type="button" ?disabled=${this._editSaving} @click=${()=>this._saveEdit()}>
            ${this._editSaving?B`<ha-icon icon="mdi:loading" style="animation:spin .8s linear infinite"></ha-icon>`:q}
            ${this._t("action.save")}
          </button>
        </div>
      </div>
    </div>`}_renderDialog(){const t=this._rooms(),e=this._categories(),i=this._config.persons??[],o=()=>this._dialogOpen=!1;return B`<div class="overlay" @click=${o}>
      <form class="dialog" @click=${t=>t.stopPropagation()} @submit=${async t=>{t.preventDefault();const e=t.target.closest("form"),i=new FormData(e),r=String(i.get("title")??"").trim();if(!r)return void e.querySelector("[name=title]")?.focus();const s=String(i.get("visibility_mode")||"all_enabled_persons"),n=String(i.get("assignment_mode")||"random"),a=String(i.get("calendar_export_entity_id")||"").trim()||void 0,l={title:r,description:String(i.get("description")||"")||void 0,room:String(i.get("room")||"")||void 0,category:String(i.get("category")||"")||void 0,importance:String(i.get("importance")||"normal"),estimated_duration_minutes:i.get("duration")?Number(i.get("duration")):void 0,due_date:String(i.get("due_date")||"")||void 0,visibility_mode:s,visibility_persons:"selected_persons"===s?i.getAll("visibility_persons").map(String):void 0,assignment_mode:n,assignment_person:"assigned"===n&&String(i.get("assignment_person")||"")||void 0,calendar_export_entity_id:a};try{await this._createTask(l),o()}catch(t){console.error("[choreflow] create_task",t)}}}>
        <div class="dlg-head">
          <span>${this._t("create.title")}</span>
          <button type="button" class="icon-btn" aria-label=${this._t("action.close")} @click=${o}><ha-icon icon="mdi:close"></ha-icon></button>
        </div>
        <div class="dlg-body">
          <label>${this._t("field.title")}<input name="title" placeholder=${this._t("create.title_placeholder")} autofocus /></label>
          <div class="two">
            <label>${this._t("field.room")}<input name="room" list="cf-rooms" placeholder=${this._t("create.room_placeholder")} /></label>
            <label>${this._t("field.category")}<input name="category" list="cf-cats" placeholder=${this._t("create.category_placeholder")} /></label>
          </div>
          <datalist id="cf-rooms">${t.map(t=>B`<option value=${t}></option>`)}</datalist>
          <datalist id="cf-cats">${e.map(t=>B`<option value=${t}></option>`)}</datalist>
          <fieldset class="radios">
            <legend>${this._t("field.importance")}</legend>
            ${["low","normal","high"].map((t,e)=>B`<label class="radio"><input type="radio" name="importance" value=${t} ?checked=${1===e} />${this._t(`importance.${t}`)}</label>`)}
          </fieldset>
          <div class="two">
            <label>${this._t("field.duration")}<input name="duration" type="number" min="0" placeholder="15" /></label>
            <label>${this._t("create.due")}<input name="due_date" type="date" /></label>
          </div>
          <details>
            <summary>${this._t("create.visibility_assignment")}</summary>
            <fieldset class="radios">
              <legend>${this._t("create.visible_to")}</legend>
              <label class="radio"><input type="radio" name="visibility_mode" value="all_enabled_persons" checked />${this._t("create.all_persons")}</label>
              <label class="radio"><input type="radio" name="visibility_mode" value="selected_persons" />${this._t("create.selected")}</label>
            </fieldset>
            ${i.length?B`<div class="chips">
                  ${i.map(t=>B`<label class="chip-check"><input type="checkbox" name="visibility_persons" value=${t.entity} />${this._personName(t)}</label>`)}
                </div>`:q}
            <fieldset class="radios">
              <legend>${this._t("create.assignment")}</legend>
              <label class="radio"><input type="radio" name="assignment_mode" value="random" checked />${this._t("create.random")}</label>
              <label class="radio"><input type="radio" name="assignment_mode" value="assigned" />${this._t("create.fixed_person")}</label>
            </fieldset>
            <label>${this._t("field.person")}<select name="assignment_person">
              <option value="">${this._t("create.choose_person")}</option>
              ${i.map(t=>B`<option value=${t.entity}>${this._personName(t)}</option>`)}
            </select></label>
          </details>
          <details>
            <summary>${this._t("create.calendar_export")}</summary>
            <label style="margin-top:8px">
              ${this._t("create.calendar_entity")}
              <input
                name="calendar_export_entity_id"
                placeholder="calendar.outlook_kalender"
                autocomplete="off"
              />
            </label>
            <p style="font-size:11px;color:var(--secondary-text-color);margin:4px 0 0">
              ${this._t("create.calendar_help")}
            </p>
          </details>
        </div>
        <div class="dlg-foot">
          <button type="button" class="btn ghost" @click=${o}>${this._t("action.cancel")}</button>
          <button type="submit" class="btn primary">${this._t("action.create_short")}</button>
        </div>
      </form>
    </div>`}};function $t(t){return"high"===t?40:"low"===t?-20:0}function xt(t,e){const i=t.states[e];return i?.attributes?.friendly_name||e.split(".").pop()||e}kt.styles=n`
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
  `,t([pt({attribute:!1})],kt.prototype,"hass",void 0),t([_t()],kt.prototype,"_config",void 0),t([_t()],kt.prototype,"_tab",void 0),t([_t()],kt.prototype,"_personFilter",void 0),t([_t()],kt.prototype,"_roomFilter",void 0),t([_t()],kt.prototype,"_categoryFilter",void 0),t([_t()],kt.prototype,"_groupByRoom",void 0),t([_t()],kt.prototype,"_dialogOpen",void 0),t([_t()],kt.prototype,"_personPickerOpen",void 0),t([_t()],kt.prototype,"_pendingAction",void 0),t([_t()],kt.prototype,"_rowState",void 0),t([_t()],kt.prototype,"_rowError",void 0),t([_t()],kt.prototype,"_tasks",void 0),t([_t()],kt.prototype,"_tasksLoading",void 0),t([_t()],kt.prototype,"_showTaskRefresh",void 0),t([_t()],kt.prototype,"_tasksError",void 0),t([_t()],kt.prototype,"_editForm",void 0),t([_t()],kt.prototype,"_editSaving",void 0),t([_t()],kt.prototype,"_editError",void 0),t([_t()],kt.prototype,"_history",void 0),t([_t()],kt.prototype,"_historyTotal",void 0),t([_t()],kt.prototype,"_historyLoading",void 0),t([_t()],kt.prototype,"_historyOffset",void 0),kt=t([dt("choreflow-card")],kt),window.customCards=window.customCards||[],window.customCards.push({type:"choreflow-card",name:"ChoreFlow Card",description:"Compact task card for the ChoreFlow integration.",preview:!0,documentationURL:"https://github.com/your-org/ha-choreflow-card"});export{kt as ChoreFlowCard};
