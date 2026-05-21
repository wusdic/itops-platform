import{D as le,k as X,an as $,y as U,l as p,ao as ne,m as k,ap as se,p as m,i as I,F as ae,j as v,aj as ie,V as ce,q as D,E as V,s as L,v as K,x as _,h as P,o as de,R as ue,aq as ge,W as he,ah as fe,ar as be,G as ve,as as me,n as E,at as G,au as J,z as Q,N as pe,U as F,A as q}from"./index-DeEsbs8n.js";import{t as ye}from"./Space-CucXZsRf.js";import{C as Ce}from"./Tooltip-D0_L80OS.js";import{f as W,a as xe}from"./use-message-CzWsbTRb.js";const Se=le&&"loading"in document.createElement("img");function ze(e={}){var o;const{root:r=null}=e;return{hash:`${e.rootMargin||"0px 0px 0px 0px"}-${Array.isArray(e.threshold)?e.threshold.join(","):(o=e.threshold)!==null&&o!==void 0?o:"0"}`,options:Object.assign(Object.assign({},e),{root:(typeof r=="string"?document.querySelector(r):r)||document.documentElement})}}const A=new WeakMap,N=new WeakMap,Y=new WeakMap,Te=(e,o,r)=>{if(!e)return()=>{};const s=ze(o),{root:d}=s.options;let n;const f=A.get(d);f?n=f:(n=new Map,A.set(d,n));let C,i;n.has(s.hash)?(i=n.get(s.hash),i[1].has(e)||(C=i[0],i[1].add(e),C.observe(e))):(C=new IntersectionObserver(T=>{T.forEach(S=>{if(S.isIntersecting){const R=N.get(S.target),z=Y.get(S.target);R&&R(),z&&(z.value=!0)}})},s.options),C.observe(e),i=[C,new Set([e])],n.set(s.hash,i));let u=!1;const x=()=>{u||(N.delete(e),Y.delete(e),u=!0,i[1].has(e)&&(i[0].unobserve(e),i[1].delete(e)),i[1].size<=0&&n.delete(s.hash),n.size||A.delete(d))};return N.set(e,x),Y.set(e,r),x};function Re(e){const{borderRadius:o,avatarColor:r,cardColor:s,fontSize:d,heightTiny:n,heightSmall:f,heightMedium:C,heightLarge:i,heightHuge:u,modalColor:x,popoverColor:T}=e;return{borderRadius:o,fontSize:d,border:`2px solid ${s}`,heightTiny:n,heightSmall:f,heightMedium:C,heightLarge:i,heightHuge:u,color:$(s,r),colorModal:$(x,r),colorPopover:$(T,r)}}const Oe={common:X,self:Re},Be=U("n-avatar-group"),_e=p("avatar",`
 width: var(--n-merged-size);
 height: var(--n-merged-size);
 color: #FFF;
 font-size: var(--n-font-size);
 display: inline-flex;
 position: relative;
 overflow: hidden;
 text-align: center;
 border: var(--n-border);
 border-radius: var(--n-border-radius);
 --n-merged-color: var(--n-color);
 background-color: var(--n-merged-color);
 transition:
 border-color .3s var(--n-bezier),
 background-color .3s var(--n-bezier),
 color .3s var(--n-bezier);
`,[ne(k("&","--n-merged-color: var(--n-color-modal);")),se(k("&","--n-merged-color: var(--n-color-popover);")),k("img",`
 width: 100%;
 height: 100%;
 `),m("text",`
 white-space: nowrap;
 display: inline-block;
 position: absolute;
 left: 50%;
 top: 50%;
 `),p("icon",`
 vertical-align: bottom;
 font-size: calc(var(--n-merged-size) - 6px);
 `),m("text","line-height: 1.25")]),we=Object.assign(Object.assign({},L.props),{size:[String,Number],src:String,circle:{type:Boolean,default:void 0},objectFit:String,round:{type:Boolean,default:void 0},bordered:{type:Boolean,default:void 0},onError:Function,fallbackSrc:String,intersectionObserverOptions:Object,lazy:Boolean,onLoad:Function,renderPlaceholder:Function,renderFallback:Function,imgProps:Object,color:String}),Ne=I({name:"Avatar",props:we,slots:Object,setup(e){const{mergedClsPrefixRef:o,inlineThemeDisabled:r}=D(e),s=P(!1);let d=null;const n=P(null),f=P(null),C=()=>{const{value:t}=n;if(t&&(d===null||d!==t.innerHTML)){d=t.innerHTML;const{value:c}=f;if(c){const{offsetWidth:b,offsetHeight:a}=c,{offsetWidth:l,offsetHeight:h}=t,j=.9,w=Math.min(b/l*j,a/h*j,1);t.style.transform=`translateX(-50%) translateY(-50%) scale(${w})`}}},i=V(Be,null),u=_(()=>{const{size:t}=e;if(t)return t;const{size:c}=i||{};return c||"medium"}),x=L("Avatar","-avatar",_e,Oe,e,o),T=V(ye,null),S=_(()=>{if(i)return!0;const{round:t,circle:c}=e;return t!==void 0||c!==void 0?t||c:T?T.roundRef.value:!1}),R=_(()=>i?!0:e.bordered||!1),z=_(()=>{const t=u.value,c=S.value,b=R.value,{color:a}=e,{self:{borderRadius:l,fontSize:h,color:j,border:w,colorModal:M,colorPopover:B},common:{cubicBezierEaseInOut:re}}=x.value;let H;return typeof t=="number"?H=`${t}px`:H=x.value.self[fe("height",t)],{"--n-font-size":h,"--n-border":b?w:"none","--n-border-radius":c?"50%":l,"--n-color":a||j,"--n-color-modal":a||M,"--n-color-popover":a||B,"--n-bezier":re,"--n-merged-size":`var(--n-avatar-size-override, ${H})`}}),g=r?K("avatar",_(()=>{const t=u.value,c=S.value,b=R.value,{color:a}=e;let l="";return t&&(typeof t=="number"?l+=`a${t}`:l+=t[0]),c&&(l+="b"),b&&(l+="c"),a&&(l+=be(a)),l}),z,e):void 0,y=P(!e.lazy);de(()=>{if(e.lazy&&e.intersectionObserverOptions){let t;const c=ue(()=>{t==null||t(),t=void 0,e.lazy&&(t=Te(f.value,e.intersectionObserverOptions,y))});ge(()=>{c(),t==null||t()})}}),he(()=>{var t;return e.src||((t=e.imgProps)===null||t===void 0?void 0:t.src)},()=>{s.value=!1});const O=P(!e.lazy);return{textRef:n,selfRef:f,mergedRoundRef:S,mergedClsPrefix:o,fitTextTransform:C,cssVars:r?void 0:z,themeClass:g==null?void 0:g.themeClass,onRender:g==null?void 0:g.onRender,hasLoadError:s,shouldStartLoading:y,loaded:O,mergedOnError:t=>{if(!y.value)return;s.value=!0;const{onError:c,imgProps:{onError:b}={}}=e;c==null||c(t),b==null||b(t)},mergedOnLoad:t=>{const{onLoad:c,imgProps:{onLoad:b}={}}=e;c==null||c(t),b==null||b(t),O.value=!0}}},render(){var e,o;const{$slots:r,src:s,mergedClsPrefix:d,lazy:n,onRender:f,loaded:C,hasLoadError:i,imgProps:u={}}=this;f==null||f();let x;const T=!C&&!i&&(this.renderPlaceholder?this.renderPlaceholder():(o=(e=this.$slots).placeholder)===null||o===void 0?void 0:o.call(e));return this.hasLoadError?x=this.renderFallback?this.renderFallback():ae(r.fallback,()=>[v("img",{src:this.fallbackSrc,style:{objectFit:this.objectFit}})]):x=ie(r.default,S=>{if(S)return v(ce,{onResize:this.fitTextTransform},{default:()=>v("span",{ref:"textRef",class:`${d}-avatar__text`},S)});if(s||u.src){const R=this.src||u.src;return v("img",Object.assign(Object.assign({},u),{loading:Se&&!this.intersectionObserverOptions&&n?"lazy":"eager",src:n&&this.intersectionObserverOptions?this.shouldStartLoading?R:void 0:R,"data-image-src":R,onLoad:this.mergedOnLoad,onError:this.mergedOnError,style:[u.style||"",{objectFit:this.objectFit},T?{height:"0",width:"0",visibility:"hidden",position:"absolute"}:""]}))}}),v("span",{ref:"selfRef",class:[`${d}-avatar`,this.themeClass],style:this.cssVars},x,n&&T)}});function Pe(e){const{baseColor:o,textColor2:r,bodyColor:s,cardColor:d,dividerColor:n,actionColor:f,scrollbarColor:C,scrollbarColorHover:i,invertedColor:u}=e;return{textColor:r,textColorInverted:"#FFF",color:s,colorEmbedded:f,headerColor:d,headerColorInverted:u,footerColor:f,footerColorInverted:u,headerBorderColor:n,headerBorderColorInverted:u,footerBorderColor:n,footerBorderColorInverted:u,siderBorderColor:n,siderBorderColorInverted:u,siderColor:d,siderColorInverted:u,siderToggleButtonBorder:`1px solid ${n}`,siderToggleButtonColor:o,siderToggleButtonIconColor:r,siderToggleButtonIconColorInverted:r,siderToggleBarColor:$(s,C),siderToggleBarColorHover:$(s,i),__invertScrollbar:"true"}}const Z=ve({name:"Layout",common:X,peers:{Scrollbar:me},self:Pe}),je=U("n-layout-sider"),ee={type:String,default:"static"},Ee=p("layout",`
 color: var(--n-text-color);
 background-color: var(--n-color);
 box-sizing: border-box;
 position: relative;
 z-index: auto;
 flex: auto;
 overflow: hidden;
 transition:
 box-shadow .3s var(--n-bezier),
 background-color .3s var(--n-bezier),
 color .3s var(--n-bezier);
`,[p("layout-scroll-container",`
 overflow-x: hidden;
 box-sizing: border-box;
 height: 100%;
 `),E("absolute-positioned",`
 position: absolute;
 left: 0;
 right: 0;
 top: 0;
 bottom: 0;
 `)]),ke={embedded:Boolean,position:ee,nativeScrollbar:{type:Boolean,default:!0},scrollbarProps:Object,onScroll:Function,contentClass:String,contentStyle:{type:[String,Object],default:""},hasSider:Boolean,siderPlacement:{type:String,default:"left"}},oe=U("n-layout");function te(e){return I({name:e?"LayoutContent":"Layout",props:Object.assign(Object.assign({},L.props),ke),setup(o){const r=P(null),s=P(null),{mergedClsPrefixRef:d,inlineThemeDisabled:n}=D(o),f=L("Layout","-layout",Ee,Z,o,d);function C(g,y){if(o.nativeScrollbar){const{value:O}=r;O&&(y===void 0?O.scrollTo(g):O.scrollTo(g,y))}else{const{value:O}=s;O&&O.scrollTo(g,y)}}Q(oe,o);let i=0,u=0;const x=g=>{var y;const O=g.target;i=O.scrollLeft,u=O.scrollTop,(y=o.onScroll)===null||y===void 0||y.call(o,g)};J(()=>{if(o.nativeScrollbar){const g=r.value;g&&(g.scrollTop=u,g.scrollLeft=i)}});const T={display:"flex",flexWrap:"nowrap",width:"100%",flexDirection:"row"},S={scrollTo:C},R=_(()=>{const{common:{cubicBezierEaseInOut:g},self:y}=f.value;return{"--n-bezier":g,"--n-color":o.embedded?y.colorEmbedded:y.color,"--n-text-color":y.textColor}}),z=n?K("layout",_(()=>o.embedded?"e":""),R,o):void 0;return Object.assign({mergedClsPrefix:d,scrollableElRef:r,scrollbarInstRef:s,hasSiderStyle:T,mergedTheme:f,handleNativeElScroll:x,cssVars:n?void 0:R,themeClass:z==null?void 0:z.themeClass,onRender:z==null?void 0:z.onRender},S)},render(){var o;const{mergedClsPrefix:r,hasSider:s}=this;(o=this.onRender)===null||o===void 0||o.call(this);const d=s?this.hasSiderStyle:void 0,n=[this.themeClass,e&&`${r}-layout-content`,`${r}-layout`,`${r}-layout--${this.position}-positioned`];return v("div",{class:n,style:this.cssVars},this.nativeScrollbar?v("div",{ref:"scrollableElRef",class:[`${r}-layout-scroll-container`,this.contentClass],style:[this.contentStyle,d],onScroll:this.handleNativeElScroll},this.$slots):v(G,Object.assign({},this.scrollbarProps,{onScroll:this.onScroll,ref:"scrollbarInstRef",theme:this.mergedTheme.peers.Scrollbar,themeOverrides:this.mergedTheme.peerOverrides.Scrollbar,contentClass:this.contentClass,contentStyle:[this.contentStyle,d]}),this.$slots))}})}const Ye=te(!1),Ve=te(!0),Le=p("layout-sider",`
 flex-shrink: 0;
 box-sizing: border-box;
 position: relative;
 z-index: 1;
 color: var(--n-text-color);
 transition:
 color .3s var(--n-bezier),
 border-color .3s var(--n-bezier),
 min-width .3s var(--n-bezier),
 max-width .3s var(--n-bezier),
 transform .3s var(--n-bezier),
 background-color .3s var(--n-bezier);
 background-color: var(--n-color);
 display: flex;
 justify-content: flex-end;
`,[E("bordered",[m("border",`
 content: "";
 position: absolute;
 top: 0;
 bottom: 0;
 width: 1px;
 background-color: var(--n-border-color);
 transition: background-color .3s var(--n-bezier);
 `)]),m("left-placement",[E("bordered",[m("border",`
 right: 0;
 `)])]),E("right-placement",`
 justify-content: flex-start;
 `,[E("bordered",[m("border",`
 left: 0;
 `)]),E("collapsed",[p("layout-toggle-button",[p("base-icon",`
 transform: rotate(180deg);
 `)]),p("layout-toggle-bar",[k("&:hover",[m("top",{transform:"rotate(-12deg) scale(1.15) translateY(-2px)"}),m("bottom",{transform:"rotate(12deg) scale(1.15) translateY(2px)"})])])]),p("layout-toggle-button",`
 left: 0;
 transform: translateX(-50%) translateY(-50%);
 `,[p("base-icon",`
 transform: rotate(0);
 `)]),p("layout-toggle-bar",`
 left: -28px;
 transform: rotate(180deg);
 `,[k("&:hover",[m("top",{transform:"rotate(12deg) scale(1.15) translateY(-2px)"}),m("bottom",{transform:"rotate(-12deg) scale(1.15) translateY(2px)"})])])]),E("collapsed",[p("layout-toggle-bar",[k("&:hover",[m("top",{transform:"rotate(-12deg) scale(1.15) translateY(-2px)"}),m("bottom",{transform:"rotate(12deg) scale(1.15) translateY(2px)"})])]),p("layout-toggle-button",[p("base-icon",`
 transform: rotate(0);
 `)])]),p("layout-toggle-button",`
 transition:
 color .3s var(--n-bezier),
 right .3s var(--n-bezier),
 left .3s var(--n-bezier),
 border-color .3s var(--n-bezier),
 background-color .3s var(--n-bezier);
 cursor: pointer;
 width: 24px;
 height: 24px;
 position: absolute;
 top: 50%;
 right: 0;
 border-radius: 50%;
 display: flex;
 align-items: center;
 justify-content: center;
 font-size: 18px;
 color: var(--n-toggle-button-icon-color);
 border: var(--n-toggle-button-border);
 background-color: var(--n-toggle-button-color);
 box-shadow: 0 2px 4px 0px rgba(0, 0, 0, .06);
 transform: translateX(50%) translateY(-50%);
 z-index: 1;
 `,[p("base-icon",`
 transition: transform .3s var(--n-bezier);
 transform: rotate(180deg);
 `)]),p("layout-toggle-bar",`
 cursor: pointer;
 height: 72px;
 width: 32px;
 position: absolute;
 top: calc(50% - 36px);
 right: -28px;
 `,[m("top, bottom",`
 position: absolute;
 width: 4px;
 border-radius: 2px;
 height: 38px;
 left: 14px;
 transition: 
 background-color .3s var(--n-bezier),
 transform .3s var(--n-bezier);
 `),m("bottom",`
 position: absolute;
 top: 34px;
 `),k("&:hover",[m("top",{transform:"rotate(12deg) scale(1.15) translateY(-2px)"}),m("bottom",{transform:"rotate(-12deg) scale(1.15) translateY(2px)"})]),m("top, bottom",{backgroundColor:"var(--n-toggle-bar-color)"}),k("&:hover",[m("top, bottom",{backgroundColor:"var(--n-toggle-bar-color-hover)"})])]),m("border",`
 position: absolute;
 top: 0;
 right: 0;
 bottom: 0;
 width: 1px;
 transition: background-color .3s var(--n-bezier);
 `),p("layout-sider-scroll-container",`
 flex-grow: 1;
 flex-shrink: 0;
 box-sizing: border-box;
 height: 100%;
 opacity: 0;
 transition: opacity .3s var(--n-bezier);
 max-width: 100%;
 `),E("show-content",[p("layout-sider-scroll-container",{opacity:1})]),E("absolute-positioned",`
 position: absolute;
 left: 0;
 top: 0;
 bottom: 0;
 `)]),$e=I({props:{clsPrefix:{type:String,required:!0},onClick:Function},render(){const{clsPrefix:e}=this;return v("div",{onClick:this.onClick,class:`${e}-layout-toggle-bar`},v("div",{class:`${e}-layout-toggle-bar__top`}),v("div",{class:`${e}-layout-toggle-bar__bottom`}))}}),Ie=I({name:"LayoutToggleButton",props:{clsPrefix:{type:String,required:!0},onClick:Function},render(){const{clsPrefix:e}=this;return v("div",{class:`${e}-layout-toggle-button`,onClick:this.onClick},v(pe,{clsPrefix:e},{default:()=>v(Ce,null)}))}}),Fe={position:ee,bordered:Boolean,collapsedWidth:{type:Number,default:48},width:{type:[Number,String],default:272},contentClass:String,contentStyle:{type:[String,Object],default:""},collapseMode:{type:String,default:"transform"},collapsed:{type:Boolean,default:void 0},defaultCollapsed:Boolean,showCollapsedContent:{type:Boolean,default:!0},showTrigger:{type:[Boolean,String],default:!1},nativeScrollbar:{type:Boolean,default:!0},inverted:Boolean,scrollbarProps:Object,triggerClass:String,triggerStyle:[String,Object],collapsedTriggerClass:String,collapsedTriggerStyle:[String,Object],"onUpdate:collapsed":[Function,Array],onUpdateCollapsed:[Function,Array],onAfterEnter:Function,onAfterLeave:Function,onExpand:[Function,Array],onCollapse:[Function,Array],onScroll:Function},Ue=I({name:"LayoutSider",props:Object.assign(Object.assign({},L.props),Fe),setup(e){const o=V(oe),r=P(null),s=P(null),d=P(e.defaultCollapsed),n=xe(q(e,"collapsed"),d),f=_(()=>W(n.value?e.collapsedWidth:e.width)),C=_(()=>e.collapseMode!=="transform"?{}:{minWidth:W(e.width)}),i=_(()=>o?o.siderPlacement:"left");function u(a,l){if(e.nativeScrollbar){const{value:h}=r;h&&(l===void 0?h.scrollTo(a):h.scrollTo(a,l))}else{const{value:h}=s;h&&h.scrollTo(a,l)}}function x(){const{"onUpdate:collapsed":a,onUpdateCollapsed:l,onExpand:h,onCollapse:j}=e,{value:w}=n;l&&F(l,!w),a&&F(a,!w),d.value=!w,w?h&&F(h):j&&F(j)}let T=0,S=0;const R=a=>{var l;const h=a.target;T=h.scrollLeft,S=h.scrollTop,(l=e.onScroll)===null||l===void 0||l.call(e,a)};J(()=>{if(e.nativeScrollbar){const a=r.value;a&&(a.scrollTop=S,a.scrollLeft=T)}}),Q(je,{collapsedRef:n,collapseModeRef:q(e,"collapseMode")});const{mergedClsPrefixRef:z,inlineThemeDisabled:g}=D(e),y=L("Layout","-layout-sider",Le,Z,e,z);function O(a){var l,h;a.propertyName==="max-width"&&(n.value?(l=e.onAfterLeave)===null||l===void 0||l.call(e):(h=e.onAfterEnter)===null||h===void 0||h.call(e))}const t={scrollTo:u},c=_(()=>{const{common:{cubicBezierEaseInOut:a},self:l}=y.value,{siderToggleButtonColor:h,siderToggleButtonBorder:j,siderToggleBarColor:w,siderToggleBarColorHover:M}=l,B={"--n-bezier":a,"--n-toggle-button-color":h,"--n-toggle-button-border":j,"--n-toggle-bar-color":w,"--n-toggle-bar-color-hover":M};return e.inverted?(B["--n-color"]=l.siderColorInverted,B["--n-text-color"]=l.textColorInverted,B["--n-border-color"]=l.siderBorderColorInverted,B["--n-toggle-button-icon-color"]=l.siderToggleButtonIconColorInverted,B.__invertScrollbar=l.__invertScrollbar):(B["--n-color"]=l.siderColor,B["--n-text-color"]=l.textColor,B["--n-border-color"]=l.siderBorderColor,B["--n-toggle-button-icon-color"]=l.siderToggleButtonIconColor),B}),b=g?K("layout-sider",_(()=>e.inverted?"a":"b"),c,e):void 0;return Object.assign({scrollableElRef:r,scrollbarInstRef:s,mergedClsPrefix:z,mergedTheme:y,styleMaxWidth:f,mergedCollapsed:n,scrollContainerStyle:C,siderPlacement:i,handleNativeElScroll:R,handleTransitionend:O,handleTriggerClick:x,inlineThemeDisabled:g,cssVars:c,themeClass:b==null?void 0:b.themeClass,onRender:b==null?void 0:b.onRender},t)},render(){var e;const{mergedClsPrefix:o,mergedCollapsed:r,showTrigger:s}=this;return(e=this.onRender)===null||e===void 0||e.call(this),v("aside",{class:[`${o}-layout-sider`,this.themeClass,`${o}-layout-sider--${this.position}-positioned`,`${o}-layout-sider--${this.siderPlacement}-placement`,this.bordered&&`${o}-layout-sider--bordered`,r&&`${o}-layout-sider--collapsed`,(!r||this.showCollapsedContent)&&`${o}-layout-sider--show-content`],onTransitionend:this.handleTransitionend,style:[this.inlineThemeDisabled?void 0:this.cssVars,{maxWidth:this.styleMaxWidth,width:W(this.width)}]},this.nativeScrollbar?v("div",{class:[`${o}-layout-sider-scroll-container`,this.contentClass],onScroll:this.handleNativeElScroll,style:[this.scrollContainerStyle,{overflow:"auto"},this.contentStyle],ref:"scrollableElRef"},this.$slots):v(G,Object.assign({},this.scrollbarProps,{onScroll:this.onScroll,ref:"scrollbarInstRef",style:this.scrollContainerStyle,contentStyle:this.contentStyle,contentClass:this.contentClass,theme:this.mergedTheme.peers.Scrollbar,themeOverrides:this.mergedTheme.peerOverrides.Scrollbar,builtinThemeOverrides:this.inverted&&this.cssVars.__invertScrollbar==="true"?{colorHover:"rgba(255, 255, 255, .4)",color:"rgba(255, 255, 255, .3)"}:void 0}),this.$slots),s?s==="bar"?v($e,{clsPrefix:o,class:r?this.collapsedTriggerClass:this.triggerClass,style:r?this.collapsedTriggerStyle:this.triggerStyle,onClick:this.handleTriggerClick}):v(Ie,{clsPrefix:o,class:r?this.collapsedTriggerClass:this.triggerClass,style:r?this.collapsedTriggerStyle:this.triggerStyle,onClick:this.handleTriggerClick}):null,this.bordered?v("div",{class:`${o}-layout-sider__border`}):null)}});export{Ye as _,je as a,Ne as b,Ue as c,Ve as d,Z as l,ee as p};
