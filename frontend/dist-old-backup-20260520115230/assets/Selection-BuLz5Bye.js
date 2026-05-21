import{O as ae,y as W,i as w,A as _t,j as se,F as Mt,k as d,V as me,U as Wt,bu as Bt,o as be,c2 as At,b9 as Ht,b3 as we,C as J,a$ as ee,c3 as ue,X as ie,ae as Lt,H as Dt,l as Nt,I as Y,n as oe,m,q as y,J as xe,p as G,c4 as jt,P as Vt,L as le,s as Kt,av as Ut,v as Ce,S as Xt,x as qt,a5 as Yt,ad as ye,b1 as Ie}from"./index-DeHMpJ-Y.js";import{e as Gt,d as Jt,f as he,p as Qt,N as Zt}from"./Popover-CyJrbRE-.js";import{N as en}from"./Input-AcI9pgdT.js";import{a as fe}from"./Space-hnrwQ-ZK.js";import{V as Se,g as Re}from"./create-jtZOmn-a.js";function Te(e){return e&-e}class ze{constructor(r,a){this.l=r,this.min=a;const c=new Array(r+1);for(let s=0;s<r+1;++s)c[s]=0;this.ft=c}add(r,a){if(a===0)return;const{l:c,ft:s}=this;for(r+=1;r<=c;)s[r]+=a,r+=Te(r)}get(r){return this.sum(r+1)-this.sum(r)}sum(r){if(r===void 0&&(r=this.l),r<=0)return 0;const{ft:a,min:c,l:s}=this;if(r>s)throw new Error("[FinweckTree.sum]: `i` is larger than length.");let u=r*c;for(;r>0;)u+=a[r],r-=Te(r);return u}getBound(r){let a=0,c=this.l;for(;c>a;){const s=Math.floor((a+c)/2),u=this.sum(s);if(u>r){c=s;continue}else if(u<r){if(a===s)return this.sum(a+1)<=r?a+1:s;a=s}else return s}return a}}let re;function tn(){return typeof document>"u"?!1:(re===void 0&&("matchMedia"in window?re=window.matchMedia("(pointer:coarse)").matches:re=!1),re)}let ve;function Fe(){return typeof document>"u"?1:(ve===void 0&&(ve="chrome"in window?window.devicePixelRatio:1),ve)}const Ee="VVirtualListXScroll";function nn({columnsRef:e,renderColRef:r,renderItemWithColsRef:a}){const c=w(0),s=w(0),u=W(()=>{const h=e.value;if(h.length===0)return null;const v=new ze(h.length,0);return h.forEach((p,I)=>{v.add(I,p.width)}),v}),g=ae(()=>{const h=u.value;return h!==null?Math.max(h.getBound(s.value)-1,0):0}),l=h=>{const v=u.value;return v!==null?v.sum(h):0},f=ae(()=>{const h=u.value;return h!==null?Math.min(h.getBound(s.value+c.value)+1,e.value.length-1):0});return _t(Ee,{startIndexRef:g,endIndexRef:f,columnsRef:e,renderColRef:r,renderItemWithColsRef:a,getLeft:l}),{listWidthRef:c,scrollLeftRef:s}}const $e=se({name:"VirtualListRow",props:{index:{type:Number,required:!0},item:{type:Object,required:!0}},setup(){const{startIndexRef:e,endIndexRef:r,columnsRef:a,getLeft:c,renderColRef:s,renderItemWithColsRef:u}=Mt(Ee);return{startIndex:e,endIndex:r,columns:a,renderCol:s,renderItemWithCols:u,getLeft:c}},render(){const{startIndex:e,endIndex:r,columns:a,renderCol:c,renderItemWithCols:s,getLeft:u,item:g}=this;if(s!=null)return s({itemIndex:this.index,startColIndex:e,endColIndex:r,allColumns:a,item:g,getLeft:u});if(c!=null){const l=[];for(let f=e;f<=r;++f){const h=a[f];l.push(c({column:h,left:u(f),item:g}))}return l}return null}}),on=he(".v-vl",{maxHeight:"inherit",height:"100%",overflow:"auto",minWidth:"1px"},[he("&:not(.v-vl--show-scrollbar)",{scrollbarWidth:"none"},[he("&::-webkit-scrollbar, &::-webkit-scrollbar-track-piece, &::-webkit-scrollbar-thumb",{width:0,height:0,display:"none"})])]),bn=se({name:"VirtualList",inheritAttrs:!1,props:{showScrollbar:{type:Boolean,default:!0},columns:{type:Array,default:()=>[]},renderCol:Function,renderItemWithCols:Function,items:{type:Array,default:()=>[]},itemSize:{type:Number,required:!0},itemResizable:Boolean,itemsStyle:[String,Object],visibleItemsTag:{type:[String,Object],default:"div"},visibleItemsProps:Object,ignoreItemResize:Boolean,onScroll:Function,onWheel:Function,onResize:Function,defaultScrollKey:[Number,String],defaultScrollIndex:Number,keyField:{type:String,default:"key"},paddingTop:{type:[Number,String],default:0},paddingBottom:{type:[Number,String],default:0}},setup(e){const r=Bt();on.mount({id:"vueuc/virtual-list",head:!0,anchorMetaName:Gt,ssr:r}),be(()=>{const{defaultScrollIndex:n,defaultScrollKey:i}=e;n!=null?k({index:n}):i!=null&&k({key:i})});let a=!1,c=!1;At(()=>{if(a=!1,!c){c=!0;return}k({top:S.value,left:g.value})}),Ht(()=>{a=!0,c||(c=!0)});const s=ae(()=>{if(e.renderCol==null&&e.renderItemWithCols==null||e.columns.length===0)return;let n=0;return e.columns.forEach(i=>{n+=i.width}),n}),u=W(()=>{const n=new Map,{keyField:i}=e;return e.items.forEach((b,C)=>{n.set(b[i],C)}),n}),{scrollLeftRef:g,listWidthRef:l}=nn({columnsRef:J(e,"columns"),renderColRef:J(e,"renderCol"),renderItemWithColsRef:J(e,"renderItemWithCols")}),f=w(null),h=w(void 0),v=new Map,p=W(()=>{const{items:n,itemSize:i,keyField:b}=e,C=new ze(n.length,i);return n.forEach((R,z)=>{const x=R[b],E=v.get(x);E!==void 0&&C.add(z,E)}),C}),I=w(0),S=w(0),O=ae(()=>Math.max(p.value.getBound(S.value-we(e.paddingTop))-1,0)),P=W(()=>{const{value:n}=h;if(n===void 0)return[];const{items:i,itemSize:b}=e,C=O.value,R=Math.min(C+Math.ceil(n/b+1),i.length-1),z=[];for(let x=C;x<=R;++x)z.push(i[x]);return z}),k=(n,i)=>{if(typeof n=="number"){B(n,i,"auto");return}const{left:b,top:C,index:R,key:z,position:x,behavior:E,debounce:M=!0}=n;if(b!==void 0||C!==void 0)B(b,C,E);else if(R!==void 0)_(R,E,M);else if(z!==void 0){const Q=u.value.get(z);Q!==void 0&&_(Q,E,M)}else x==="bottom"?B(0,Number.MAX_SAFE_INTEGER,E):x==="top"&&B(0,0,E)};let F,$=null;function _(n,i,b){const{value:C}=p,R=C.sum(n)+we(e.paddingTop);if(!b)f.value.scrollTo({left:0,top:R,behavior:i});else{F=n,$!==null&&window.clearTimeout($),$=window.setTimeout(()=>{F=void 0,$=null},16);const{scrollTop:z,offsetHeight:x}=f.value;if(R>z){const E=C.get(n);R+E<=z+x||f.value.scrollTo({left:0,top:R+E-x,behavior:i})}else f.value.scrollTo({left:0,top:R,behavior:i})}}function B(n,i,b){f.value.scrollTo({left:n,top:i,behavior:b})}function H(n,i){var b,C,R;if(a||e.ignoreItemResize||N(i.target))return;const{value:z}=p,x=u.value.get(n),E=z.get(x),M=(R=(C=(b=i.borderBoxSize)===null||b===void 0?void 0:b[0])===null||C===void 0?void 0:C.blockSize)!==null&&R!==void 0?R:i.contentRect.height;if(M===E)return;M-e.itemSize===0?v.delete(n):v.set(n,M-e.itemSize);const j=M-E;if(j===0)return;z.add(x,j);const V=f.value;if(V!=null){if(F===void 0){const Z=z.sum(x);V.scrollTop>Z&&V.scrollBy(0,j)}else if(x<F)V.scrollBy(0,j);else if(x===F){const Z=z.sum(x);M+Z>V.scrollTop+V.offsetHeight&&V.scrollBy(0,j)}D()}I.value++}const A=!tn();let L=!1;function K(n){var i;(i=e.onScroll)===null||i===void 0||i.call(e,n),(!A||!L)&&D()}function U(n){var i;if((i=e.onWheel)===null||i===void 0||i.call(e,n),A){const b=f.value;if(b!=null){if(n.deltaX===0&&(b.scrollTop===0&&n.deltaY<=0||b.scrollTop+b.offsetHeight>=b.scrollHeight&&n.deltaY>=0))return;n.preventDefault(),b.scrollTop+=n.deltaY/Fe(),b.scrollLeft+=n.deltaX/Fe(),D(),L=!0,Jt(()=>{L=!1})}}}function X(n){if(a||N(n.target))return;if(e.renderCol==null&&e.renderItemWithCols==null){if(n.contentRect.height===h.value)return}else if(n.contentRect.height===h.value&&n.contentRect.width===l.value)return;h.value=n.contentRect.height,l.value=n.contentRect.width;const{onResize:i}=e;i!==void 0&&i(n)}function D(){const{value:n}=f;n!=null&&(S.value=n.scrollTop,g.value=n.scrollLeft)}function N(n){let i=n;for(;i!==null;){if(i.style.display==="none")return!0;i=i.parentElement}return!1}return{listHeight:h,listStyle:{overflow:"auto"},keyToIndex:u,itemsStyle:W(()=>{const{itemResizable:n}=e,i=ee(p.value.sum());return I.value,[e.itemsStyle,{boxSizing:"content-box",width:ee(s.value),height:n?"":i,minHeight:n?i:"",paddingTop:ee(e.paddingTop),paddingBottom:ee(e.paddingBottom)}]}),visibleItemsStyle:W(()=>(I.value,{transform:`translateY(${ee(p.value.sum(O.value))})`})),viewportItems:P,listElRef:f,itemsElRef:w(null),scrollTo:k,handleListResize:X,handleListScroll:K,handleListWheel:U,handleItemResize:H}},render(){const{itemResizable:e,keyField:r,keyToIndex:a,visibleItemsTag:c}=this;return d(me,{onResize:this.handleListResize},{default:()=>{var s,u;return d("div",Wt(this.$attrs,{class:["v-vl",this.showScrollbar&&"v-vl--show-scrollbar"],onScroll:this.handleListScroll,onWheel:this.handleListWheel,ref:"listElRef"}),[this.items.length!==0?d("div",{ref:"itemsElRef",class:"v-vl-items",style:this.itemsStyle},[d(c,Object.assign({class:"v-vl-visible-items",style:this.visibleItemsStyle},this.visibleItemsProps),{default:()=>{const{renderCol:g,renderItemWithCols:l}=this;return this.viewportItems.map(f=>{const h=f[r],v=a.get(h),p=g!=null?d($e,{index:v,item:f}):void 0,I=l!=null?d($e,{index:v,item:f}):void 0,S=this.$slots.default({item:f,renderedCols:p,renderedItemWithCols:I,index:v})[0];return e?d(me,{key:h,onResize:O=>this.handleItemResize(h,O)},{default:()=>S}):(S.key=h,S)})}})]):(u=(s=this.$slots).empty)===null||u===void 0?void 0:u.call(s)])}})}});function ln(e,r){r&&(be(()=>{const{value:a}=e;a&&ue.registerHandler(a,r)}),ie(e,(a,c)=>{c&&ue.unregisterHandler(c)},{deep:!1}),Lt(()=>{const{value:a}=e;a&&ue.unregisterHandler(a)}))}const gn=se({props:{onFocus:Function,onBlur:Function},setup(e){return()=>d("div",{style:"width: 0; height: 0",tabindex:0,onFocus:e.onFocus,onBlur:e.onBlur})}}),rn={paddingSingle:"0 26px 0 12px",paddingMultiple:"3px 26px 0 12px",clearSize:"16px",arrowSize:"16px"};function an(e){const{borderRadius:r,textColor2:a,textColorDisabled:c,inputColor:s,inputColorDisabled:u,primaryColor:g,primaryColorHover:l,warningColor:f,warningColorHover:h,errorColor:v,errorColorHover:p,borderColor:I,iconColor:S,iconColorDisabled:O,clearColor:P,clearColorHover:k,clearColorPressed:F,placeholderColor:$,placeholderColorDisabled:_,fontSizeTiny:B,fontSizeSmall:H,fontSizeMedium:A,fontSizeLarge:L,heightTiny:K,heightSmall:U,heightMedium:X,heightLarge:D,fontWeight:N}=e;return Object.assign(Object.assign({},rn),{fontSizeTiny:B,fontSizeSmall:H,fontSizeMedium:A,fontSizeLarge:L,heightTiny:K,heightSmall:U,heightMedium:X,heightLarge:D,borderRadius:r,fontWeight:N,textColor:a,textColorDisabled:c,placeholderColor:$,placeholderColorDisabled:_,color:s,colorDisabled:u,colorActive:s,border:`1px solid ${I}`,borderHover:`1px solid ${l}`,borderActive:`1px solid ${g}`,borderFocus:`1px solid ${l}`,boxShadowHover:"none",boxShadowActive:`0 0 0 2px ${Y(g,{alpha:.2})}`,boxShadowFocus:`0 0 0 2px ${Y(g,{alpha:.2})}`,caretColor:g,arrowColor:S,arrowColorDisabled:O,loadingColor:g,borderWarning:`1px solid ${f}`,borderHoverWarning:`1px solid ${h}`,borderActiveWarning:`1px solid ${f}`,borderFocusWarning:`1px solid ${h}`,boxShadowHoverWarning:"none",boxShadowActiveWarning:`0 0 0 2px ${Y(f,{alpha:.2})}`,boxShadowFocusWarning:`0 0 0 2px ${Y(f,{alpha:.2})}`,colorActiveWarning:s,caretColorWarning:f,borderError:`1px solid ${v}`,borderHoverError:`1px solid ${p}`,borderActiveError:`1px solid ${v}`,borderFocusError:`1px solid ${p}`,boxShadowHoverError:"none",boxShadowActiveError:`0 0 0 2px ${Y(v,{alpha:.2})}`,boxShadowFocusError:`0 0 0 2px ${Y(v,{alpha:.2})}`,colorActiveError:s,caretColorError:v,clearColor:P,clearColorHover:k,clearColorPressed:F})}const sn=Dt({name:"InternalSelection",common:Nt,peers:{Popover:Qt},self:an}),dn=oe([m("base-selection",`
 --n-padding-single: var(--n-padding-single-top) var(--n-padding-single-right) var(--n-padding-single-bottom) var(--n-padding-single-left);
 --n-padding-multiple: var(--n-padding-multiple-top) var(--n-padding-multiple-right) var(--n-padding-multiple-bottom) var(--n-padding-multiple-left);
 position: relative;
 z-index: auto;
 box-shadow: none;
 width: 100%;
 max-width: 100%;
 display: inline-block;
 vertical-align: bottom;
 border-radius: var(--n-border-radius);
 min-height: var(--n-height);
 line-height: 1.5;
 font-size: var(--n-font-size);
 `,[m("base-loading",`
 color: var(--n-loading-color);
 `),m("base-selection-tags","min-height: var(--n-height);"),y("border, state-border",`
 position: absolute;
 left: 0;
 right: 0;
 top: 0;
 bottom: 0;
 pointer-events: none;
 border: var(--n-border);
 border-radius: inherit;
 transition:
 box-shadow .3s var(--n-bezier),
 border-color .3s var(--n-bezier);
 `),y("state-border",`
 z-index: 1;
 border-color: #0000;
 `),m("base-suffix",`
 cursor: pointer;
 position: absolute;
 top: 50%;
 transform: translateY(-50%);
 right: 10px;
 `,[y("arrow",`
 font-size: var(--n-arrow-size);
 color: var(--n-arrow-color);
 transition: color .3s var(--n-bezier);
 `)]),m("base-selection-overlay",`
 display: flex;
 align-items: center;
 white-space: nowrap;
 pointer-events: none;
 position: absolute;
 top: 0;
 right: 0;
 bottom: 0;
 left: 0;
 padding: var(--n-padding-single);
 transition: color .3s var(--n-bezier);
 `,[y("wrapper",`
 flex-basis: 0;
 flex-grow: 1;
 overflow: hidden;
 text-overflow: ellipsis;
 `)]),m("base-selection-placeholder",`
 color: var(--n-placeholder-color);
 `,[y("inner",`
 max-width: 100%;
 overflow: hidden;
 `)]),m("base-selection-tags",`
 cursor: pointer;
 outline: none;
 box-sizing: border-box;
 position: relative;
 z-index: auto;
 display: flex;
 padding: var(--n-padding-multiple);
 flex-wrap: wrap;
 align-items: center;
 width: 100%;
 vertical-align: bottom;
 background-color: var(--n-color);
 border-radius: inherit;
 transition:
 color .3s var(--n-bezier),
 box-shadow .3s var(--n-bezier),
 background-color .3s var(--n-bezier);
 `),m("base-selection-label",`
 height: var(--n-height);
 display: inline-flex;
 width: 100%;
 vertical-align: bottom;
 cursor: pointer;
 outline: none;
 z-index: auto;
 box-sizing: border-box;
 position: relative;
 transition:
 color .3s var(--n-bezier),
 box-shadow .3s var(--n-bezier),
 background-color .3s var(--n-bezier);
 border-radius: inherit;
 background-color: var(--n-color);
 align-items: center;
 `,[m("base-selection-input",`
 font-size: inherit;
 line-height: inherit;
 outline: none;
 cursor: pointer;
 box-sizing: border-box;
 border:none;
 width: 100%;
 padding: var(--n-padding-single);
 background-color: #0000;
 color: var(--n-text-color);
 transition: color .3s var(--n-bezier);
 caret-color: var(--n-caret-color);
 `,[y("content",`
 text-overflow: ellipsis;
 overflow: hidden;
 white-space: nowrap; 
 `)]),y("render-label",`
 color: var(--n-text-color);
 `)]),xe("disabled",[oe("&:hover",[y("state-border",`
 box-shadow: var(--n-box-shadow-hover);
 border: var(--n-border-hover);
 `)]),G("focus",[y("state-border",`
 box-shadow: var(--n-box-shadow-focus);
 border: var(--n-border-focus);
 `)]),G("active",[y("state-border",`
 box-shadow: var(--n-box-shadow-active);
 border: var(--n-border-active);
 `),m("base-selection-label","background-color: var(--n-color-active);"),m("base-selection-tags","background-color: var(--n-color-active);")])]),G("disabled","cursor: not-allowed;",[y("arrow",`
 color: var(--n-arrow-color-disabled);
 `),m("base-selection-label",`
 cursor: not-allowed;
 background-color: var(--n-color-disabled);
 `,[m("base-selection-input",`
 cursor: not-allowed;
 color: var(--n-text-color-disabled);
 `),y("render-label",`
 color: var(--n-text-color-disabled);
 `)]),m("base-selection-tags",`
 cursor: not-allowed;
 background-color: var(--n-color-disabled);
 `),m("base-selection-placeholder",`
 cursor: not-allowed;
 color: var(--n-placeholder-color-disabled);
 `)]),m("base-selection-input-tag",`
 height: calc(var(--n-height) - 6px);
 line-height: calc(var(--n-height) - 6px);
 outline: none;
 display: none;
 position: relative;
 margin-bottom: 3px;
 max-width: 100%;
 vertical-align: bottom;
 `,[y("input",`
 font-size: inherit;
 font-family: inherit;
 min-width: 1px;
 padding: 0;
 background-color: #0000;
 outline: none;
 border: none;
 max-width: 100%;
 overflow: hidden;
 width: 1em;
 line-height: inherit;
 cursor: pointer;
 color: var(--n-text-color);
 caret-color: var(--n-caret-color);
 `),y("mirror",`
 position: absolute;
 left: 0;
 top: 0;
 white-space: pre;
 visibility: hidden;
 user-select: none;
 -webkit-user-select: none;
 opacity: 0;
 `)]),["warning","error"].map(e=>G(`${e}-status`,[y("state-border",`border: var(--n-border-${e});`),xe("disabled",[oe("&:hover",[y("state-border",`
 box-shadow: var(--n-box-shadow-hover-${e});
 border: var(--n-border-hover-${e});
 `)]),G("active",[y("state-border",`
 box-shadow: var(--n-box-shadow-active-${e});
 border: var(--n-border-active-${e});
 `),m("base-selection-label",`background-color: var(--n-color-active-${e});`),m("base-selection-tags",`background-color: var(--n-color-active-${e});`)]),G("focus",[y("state-border",`
 box-shadow: var(--n-box-shadow-focus-${e});
 border: var(--n-border-focus-${e});
 `)])])]))]),m("base-selection-popover",`
 margin-bottom: -3px;
 display: flex;
 flex-wrap: wrap;
 margin-right: -8px;
 `),m("base-selection-tag-wrapper",`
 max-width: 100%;
 display: inline-flex;
 padding: 0 7px 3px 0;
 `,[oe("&:last-child","padding-right: 0;"),m("tag",`
 font-size: 14px;
 max-width: 100%;
 `,[y("content",`
 line-height: 1.25;
 text-overflow: ellipsis;
 overflow: hidden;
 `)])])]),pn=se({name:"InternalSelection",props:Object.assign(Object.assign({},Ce.props),{clsPrefix:{type:String,required:!0},bordered:{type:Boolean,default:void 0},active:Boolean,pattern:{type:String,default:""},placeholder:String,selectedOption:{type:Object,default:null},selectedOptions:{type:Array,default:null},labelField:{type:String,default:"label"},valueField:{type:String,default:"value"},multiple:Boolean,filterable:Boolean,clearable:Boolean,disabled:Boolean,size:{type:String,default:"medium"},loading:Boolean,autofocus:Boolean,showArrow:{type:Boolean,default:!0},inputProps:Object,focused:Boolean,renderTag:Function,onKeydown:Function,onClick:Function,onBlur:Function,onFocus:Function,onDeleteOption:Function,maxTagCount:[String,Number],ellipsisTagPopoverProps:Object,onClear:Function,onPatternInput:Function,onPatternFocus:Function,onPatternBlur:Function,renderLabel:Function,status:String,inlineThemeDisabled:Boolean,ignoreComposition:{type:Boolean,default:!0},onResize:Function}),setup(e){const{mergedClsPrefixRef:r,mergedRtlRef:a}=Kt(e),c=Ut("InternalSelection",a,r),s=w(null),u=w(null),g=w(null),l=w(null),f=w(null),h=w(null),v=w(null),p=w(null),I=w(null),S=w(null),O=w(!1),P=w(!1),k=w(!1),F=Ce("InternalSelection","-internal-selection",dn,sn,e,J(e,"clsPrefix")),$=W(()=>e.clearable&&!e.disabled&&(k.value||e.active)),_=W(()=>e.selectedOption?e.renderTag?e.renderTag({option:e.selectedOption,handleClose:()=>{}}):e.renderLabel?e.renderLabel(e.selectedOption,!0):le(e.selectedOption[e.labelField],e.selectedOption,!0):e.placeholder),B=W(()=>{const t=e.selectedOption;if(t)return t[e.labelField]}),H=W(()=>e.multiple?!!(Array.isArray(e.selectedOptions)&&e.selectedOptions.length):e.selectedOption!==null);function A(){var t;const{value:o}=s;if(o){const{value:T}=u;T&&(T.style.width=`${o.offsetWidth}px`,e.maxTagCount!=="responsive"&&((t=I.value)===null||t===void 0||t.sync({showAllItemsBeforeCalculate:!1})))}}function L(){const{value:t}=S;t&&(t.style.display="none")}function K(){const{value:t}=S;t&&(t.style.display="inline-block")}ie(J(e,"active"),t=>{t||L()}),ie(J(e,"pattern"),()=>{e.multiple&&Yt(A)});function U(t){const{onFocus:o}=e;o&&o(t)}function X(t){const{onBlur:o}=e;o&&o(t)}function D(t){const{onDeleteOption:o}=e;o&&o(t)}function N(t){const{onClear:o}=e;o&&o(t)}function n(t){const{onPatternInput:o}=e;o&&o(t)}function i(t){var o;(!t.relatedTarget||!(!((o=g.value)===null||o===void 0)&&o.contains(t.relatedTarget)))&&U(t)}function b(t){var o;!((o=g.value)===null||o===void 0)&&o.contains(t.relatedTarget)||X(t)}function C(t){N(t)}function R(){k.value=!0}function z(){k.value=!1}function x(t){!e.active||!e.filterable||t.target!==u.value&&t.preventDefault()}function E(t){D(t)}const M=w(!1);function Q(t){if(t.key==="Backspace"&&!M.value&&!e.pattern.length){const{selectedOptions:o}=e;o!=null&&o.length&&E(o[o.length-1])}}let j=null;function V(t){const{value:o}=s;if(o){const T=t.target.value;o.textContent=T,A()}e.ignoreComposition&&M.value?j=t:n(t)}function Z(){M.value=!0}function Oe(){M.value=!1,e.ignoreComposition&&n(j),j=null}function Pe(t){var o;P.value=!0,(o=e.onPatternFocus)===null||o===void 0||o.call(e,t)}function ke(t){var o;P.value=!1,(o=e.onPatternBlur)===null||o===void 0||o.call(e,t)}function _e(){var t,o;if(e.filterable)P.value=!1,(t=h.value)===null||t===void 0||t.blur(),(o=u.value)===null||o===void 0||o.blur();else if(e.multiple){const{value:T}=l;T==null||T.blur()}else{const{value:T}=f;T==null||T.blur()}}function Me(){var t,o,T;e.filterable?(P.value=!1,(t=h.value)===null||t===void 0||t.focus()):e.multiple?(o=l.value)===null||o===void 0||o.focus():(T=f.value)===null||T===void 0||T.focus()}function We(){const{value:t}=u;t&&(K(),t.focus())}function Be(){const{value:t}=u;t&&t.blur()}function Ae(t){const{value:o}=v;o&&o.setTextContent(`+${t}`)}function He(){const{value:t}=p;return t}function Le(){return u.value}let de=null;function ce(){de!==null&&window.clearTimeout(de)}function De(){e.active||(ce(),de=window.setTimeout(()=>{H.value&&(O.value=!0)},100))}function Ne(){ce()}function je(t){t||(ce(),O.value=!1)}ie(H,t=>{t||(O.value=!1)}),be(()=>{Xt(()=>{const t=h.value;t&&(e.disabled?t.removeAttribute("tabindex"):t.tabIndex=P.value?-1:0)})}),ln(g,e.onResize);const{inlineThemeDisabled:ge}=e,pe=W(()=>{const{size:t}=e,{common:{cubicBezierEaseInOut:o},self:{fontWeight:T,borderRadius:Ve,color:Ke,placeholderColor:Ue,textColor:Xe,paddingSingle:qe,paddingMultiple:Ye,caretColor:Ge,colorDisabled:Je,textColorDisabled:Qe,placeholderColorDisabled:Ze,colorActive:et,boxShadowFocus:tt,boxShadowActive:nt,boxShadowHover:ot,border:lt,borderFocus:rt,borderHover:it,borderActive:at,arrowColor:st,arrowColorDisabled:dt,loadingColor:ct,colorActiveWarning:ut,boxShadowFocusWarning:ht,boxShadowActiveWarning:ft,boxShadowHoverWarning:vt,borderWarning:bt,borderFocusWarning:gt,borderHoverWarning:pt,borderActiveWarning:mt,colorActiveError:wt,boxShadowFocusError:xt,boxShadowActiveError:Ct,boxShadowHoverError:yt,borderError:It,borderFocusError:St,borderHoverError:Rt,borderActiveError:Tt,clearColor:Ft,clearColorHover:$t,clearColorPressed:zt,clearSize:Et,arrowSize:Ot,[ye("height",t)]:Pt,[ye("fontSize",t)]:kt}}=F.value,te=Ie(qe),ne=Ie(Ye);return{"--n-bezier":o,"--n-border":lt,"--n-border-active":at,"--n-border-focus":rt,"--n-border-hover":it,"--n-border-radius":Ve,"--n-box-shadow-active":nt,"--n-box-shadow-focus":tt,"--n-box-shadow-hover":ot,"--n-caret-color":Ge,"--n-color":Ke,"--n-color-active":et,"--n-color-disabled":Je,"--n-font-size":kt,"--n-height":Pt,"--n-padding-single-top":te.top,"--n-padding-multiple-top":ne.top,"--n-padding-single-right":te.right,"--n-padding-multiple-right":ne.right,"--n-padding-single-left":te.left,"--n-padding-multiple-left":ne.left,"--n-padding-single-bottom":te.bottom,"--n-padding-multiple-bottom":ne.bottom,"--n-placeholder-color":Ue,"--n-placeholder-color-disabled":Ze,"--n-text-color":Xe,"--n-text-color-disabled":Qe,"--n-arrow-color":st,"--n-arrow-color-disabled":dt,"--n-loading-color":ct,"--n-color-active-warning":ut,"--n-box-shadow-focus-warning":ht,"--n-box-shadow-active-warning":ft,"--n-box-shadow-hover-warning":vt,"--n-border-warning":bt,"--n-border-focus-warning":gt,"--n-border-hover-warning":pt,"--n-border-active-warning":mt,"--n-color-active-error":wt,"--n-box-shadow-focus-error":xt,"--n-box-shadow-active-error":Ct,"--n-box-shadow-hover-error":yt,"--n-border-error":It,"--n-border-focus-error":St,"--n-border-hover-error":Rt,"--n-border-active-error":Tt,"--n-clear-size":Et,"--n-clear-color":Ft,"--n-clear-color-hover":$t,"--n-clear-color-pressed":zt,"--n-arrow-size":Ot,"--n-font-weight":T}}),q=ge?qt("internal-selection",W(()=>e.size[0]),pe,e):void 0;return{mergedTheme:F,mergedClearable:$,mergedClsPrefix:r,rtlEnabled:c,patternInputFocused:P,filterablePlaceholder:_,label:B,selected:H,showTagsPanel:O,isComposing:M,counterRef:v,counterWrapperRef:p,patternInputMirrorRef:s,patternInputRef:u,selfRef:g,multipleElRef:l,singleElRef:f,patternInputWrapperRef:h,overflowRef:I,inputTagElRef:S,handleMouseDown:x,handleFocusin:i,handleClear:C,handleMouseEnter:R,handleMouseLeave:z,handleDeleteOption:E,handlePatternKeyDown:Q,handlePatternInputInput:V,handlePatternInputBlur:ke,handlePatternInputFocus:Pe,handleMouseEnterCounter:De,handleMouseLeaveCounter:Ne,handleFocusout:b,handleCompositionEnd:Oe,handleCompositionStart:Z,onPopoverUpdateShow:je,focus:Me,focusInput:We,blur:_e,blurInput:Be,updateCounter:Ae,getCounter:He,getTail:Le,renderLabel:e.renderLabel,cssVars:ge?void 0:pe,themeClass:q==null?void 0:q.themeClass,onRender:q==null?void 0:q.onRender}},render(){const{status:e,multiple:r,size:a,disabled:c,filterable:s,maxTagCount:u,bordered:g,clsPrefix:l,ellipsisTagPopoverProps:f,onRender:h,renderTag:v,renderLabel:p}=this;h==null||h();const I=u==="responsive",S=typeof u=="number",O=I||S,P=d(jt,null,{default:()=>d(en,{clsPrefix:l,loading:this.loading,showArrow:this.showArrow,showClear:this.mergedClearable&&this.selected,onClear:this.handleClear},{default:()=>{var F,$;return($=(F=this.$slots).arrow)===null||$===void 0?void 0:$.call(F)}})});let k;if(r){const{labelField:F}=this,$=n=>d("div",{class:`${l}-base-selection-tag-wrapper`,key:n.value},v?v({option:n,handleClose:()=>{this.handleDeleteOption(n)}}):d(fe,{size:a,closable:!n.disabled,disabled:c,onClose:()=>{this.handleDeleteOption(n)},internalCloseIsButtonTag:!1,internalCloseFocusable:!1},{default:()=>p?p(n,!0):le(n[F],n,!0)})),_=()=>(S?this.selectedOptions.slice(0,u):this.selectedOptions).map($),B=s?d("div",{class:`${l}-base-selection-input-tag`,ref:"inputTagElRef",key:"__input-tag__"},d("input",Object.assign({},this.inputProps,{ref:"patternInputRef",tabindex:-1,disabled:c,value:this.pattern,autofocus:this.autofocus,class:`${l}-base-selection-input-tag__input`,onBlur:this.handlePatternInputBlur,onFocus:this.handlePatternInputFocus,onKeydown:this.handlePatternKeyDown,onInput:this.handlePatternInputInput,onCompositionstart:this.handleCompositionStart,onCompositionend:this.handleCompositionEnd})),d("span",{ref:"patternInputMirrorRef",class:`${l}-base-selection-input-tag__mirror`},this.pattern)):null,H=I?()=>d("div",{class:`${l}-base-selection-tag-wrapper`,ref:"counterWrapperRef"},d(fe,{size:a,ref:"counterRef",onMouseenter:this.handleMouseEnterCounter,onMouseleave:this.handleMouseLeaveCounter,disabled:c})):void 0;let A;if(S){const n=this.selectedOptions.length-u;n>0&&(A=d("div",{class:`${l}-base-selection-tag-wrapper`,key:"__counter__"},d(fe,{size:a,ref:"counterRef",onMouseenter:this.handleMouseEnterCounter,disabled:c},{default:()=>`+${n}`})))}const L=I?s?d(Se,{ref:"overflowRef",updateCounter:this.updateCounter,getCounter:this.getCounter,getTail:this.getTail,style:{width:"100%",display:"flex",overflow:"hidden"}},{default:_,counter:H,tail:()=>B}):d(Se,{ref:"overflowRef",updateCounter:this.updateCounter,getCounter:this.getCounter,style:{width:"100%",display:"flex",overflow:"hidden"}},{default:_,counter:H}):S&&A?_().concat(A):_(),K=O?()=>d("div",{class:`${l}-base-selection-popover`},I?_():this.selectedOptions.map($)):void 0,U=O?Object.assign({show:this.showTagsPanel,trigger:"hover",overlap:!0,placement:"top",width:"trigger",onUpdateShow:this.onPopoverUpdateShow,theme:this.mergedTheme.peers.Popover,themeOverrides:this.mergedTheme.peerOverrides.Popover},f):null,D=(this.selected?!1:this.active?!this.pattern&&!this.isComposing:!0)?d("div",{class:`${l}-base-selection-placeholder ${l}-base-selection-overlay`},d("div",{class:`${l}-base-selection-placeholder__inner`},this.placeholder)):null,N=s?d("div",{ref:"patternInputWrapperRef",class:`${l}-base-selection-tags`},L,I?null:B,P):d("div",{ref:"multipleElRef",class:`${l}-base-selection-tags`,tabindex:c?void 0:0},L,P);k=d(Vt,null,O?d(Zt,Object.assign({},U,{scrollable:!0,style:"max-height: calc(var(--v-target-height) * 6.6);"}),{trigger:()=>N,default:K}):N,D)}else if(s){const F=this.pattern||this.isComposing,$=this.active?!F:!this.selected,_=this.active?!1:this.selected;k=d("div",{ref:"patternInputWrapperRef",class:`${l}-base-selection-label`,title:this.patternInputFocused?void 0:Re(this.label)},d("input",Object.assign({},this.inputProps,{ref:"patternInputRef",class:`${l}-base-selection-input`,value:this.active?this.pattern:"",placeholder:"",readonly:c,disabled:c,tabindex:-1,autofocus:this.autofocus,onFocus:this.handlePatternInputFocus,onBlur:this.handlePatternInputBlur,onInput:this.handlePatternInputInput,onCompositionstart:this.handleCompositionStart,onCompositionend:this.handleCompositionEnd})),_?d("div",{class:`${l}-base-selection-label__render-label ${l}-base-selection-overlay`,key:"input"},d("div",{class:`${l}-base-selection-overlay__wrapper`},v?v({option:this.selectedOption,handleClose:()=>{}}):p?p(this.selectedOption,!0):le(this.label,this.selectedOption,!0))):null,$?d("div",{class:`${l}-base-selection-placeholder ${l}-base-selection-overlay`,key:"placeholder"},d("div",{class:`${l}-base-selection-overlay__wrapper`},this.filterablePlaceholder)):null,P)}else k=d("div",{ref:"singleElRef",class:`${l}-base-selection-label`,tabindex:this.disabled?void 0:0},this.label!==void 0?d("div",{class:`${l}-base-selection-input`,title:Re(this.label),key:"input"},d("div",{class:`${l}-base-selection-input__content`},v?v({option:this.selectedOption,handleClose:()=>{}}):p?p(this.selectedOption,!0):le(this.label,this.selectedOption,!0))):d("div",{class:`${l}-base-selection-placeholder ${l}-base-selection-overlay`,key:"placeholder"},d("div",{class:`${l}-base-selection-placeholder__inner`},this.placeholder)),P);return d("div",{ref:"selfRef",class:[`${l}-base-selection`,this.rtlEnabled&&`${l}-base-selection--rtl`,this.themeClass,e&&`${l}-base-selection--${e}-status`,{[`${l}-base-selection--active`]:this.active,[`${l}-base-selection--selected`]:this.selected||this.active&&this.pattern,[`${l}-base-selection--disabled`]:this.disabled,[`${l}-base-selection--multiple`]:this.multiple,[`${l}-base-selection--focus`]:this.focused}],style:this.cssVars,onClick:this.onClick,onMouseenter:this.handleMouseEnter,onMouseleave:this.handleMouseLeave,onKeydown:this.onKeydown,onFocusin:this.handleFocusin,onFocusout:this.handleFocusout,onMousedown:this.handleMouseDown},k,g?d("div",{class:`${l}-base-selection__border`}):null,g?d("div",{class:`${l}-base-selection__state-border`}):null)}});export{gn as F,pn as N,bn as V,sn as i,ln as u};
