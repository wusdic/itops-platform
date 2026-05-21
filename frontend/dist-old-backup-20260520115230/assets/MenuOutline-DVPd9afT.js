import{H as Q,ar as Z,l as ee,as as F,z as N,m as a,p,j as w,k as d,at as A,s as W,v as O,au as V,x as H,y as C,i as k,A as U,q as n,n as B,N as oe,F as te,W as $,C as Y,e as re,c as le,a as L}from"./index-BhibVBnU.js";import{C as se}from"./ChevronRight-BVE8FlPZ.js";import{f as E,u as ne}from"./get-DktaQEnH.js";function ae(e){const{baseColor:o,textColor2:r,bodyColor:u,cardColor:b,dividerColor:i,actionColor:y,scrollbarColor:_,scrollbarColorHover:x,invertedColor:h}=e;return{textColor:r,textColorInverted:"#FFF",color:u,colorEmbedded:y,headerColor:b,headerColorInverted:h,footerColor:y,footerColorInverted:h,headerBorderColor:i,headerBorderColorInverted:h,footerBorderColor:i,footerBorderColorInverted:h,siderBorderColor:i,siderBorderColorInverted:h,siderColor:b,siderColorInverted:h,siderToggleButtonBorder:`1px solid ${i}`,siderToggleButtonColor:o,siderToggleButtonIconColor:r,siderToggleButtonIconColorInverted:r,siderToggleBarColor:F(u,_),siderToggleBarColorHover:F(u,x),__invertScrollbar:"true"}}const D=Q({name:"Layout",common:ee,peers:{Scrollbar:Z},self:ae}),ie=N("n-layout-sider"),X={type:String,default:"static"},ce=a("layout",`
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
`,[a("layout-scroll-container",`
 overflow-x: hidden;
 box-sizing: border-box;
 height: 100%;
 `),p("absolute-positioned",`
 position: absolute;
 left: 0;
 right: 0;
 top: 0;
 bottom: 0;
 `)]),de={embedded:Boolean,position:X,nativeScrollbar:{type:Boolean,default:!0},scrollbarProps:Object,onScroll:Function,contentClass:String,contentStyle:{type:[String,Object],default:""},hasSider:Boolean,siderPlacement:{type:String,default:"left"}},q=N("n-layout");function K(e){return w({name:e?"LayoutContent":"Layout",props:Object.assign(Object.assign({},O.props),de),setup(o){const r=k(null),u=k(null),{mergedClsPrefixRef:b,inlineThemeDisabled:i}=W(o),y=O("Layout","-layout",ce,D,o,b);function _(c,g){if(o.nativeScrollbar){const{value:f}=r;f&&(g===void 0?f.scrollTo(c):f.scrollTo(c,g))}else{const{value:f}=u;f&&f.scrollTo(c,g)}}U(q,o);let x=0,h=0;const j=c=>{var g;const f=c.target;x=f.scrollLeft,h=f.scrollTop,(g=o.onScroll)===null||g===void 0||g.call(o,c)};V(()=>{if(o.nativeScrollbar){const c=r.value;c&&(c.scrollTop=h,c.scrollLeft=x)}});const z={display:"flex",flexWrap:"nowrap",width:"100%",flexDirection:"row"},R={scrollTo:_},I=C(()=>{const{common:{cubicBezierEaseInOut:c},self:g}=y.value;return{"--n-bezier":c,"--n-color":o.embedded?g.colorEmbedded:g.color,"--n-text-color":g.textColor}}),m=i?H("layout",C(()=>o.embedded?"e":""),I,o):void 0;return Object.assign({mergedClsPrefix:b,scrollableElRef:r,scrollbarInstRef:u,hasSiderStyle:z,mergedTheme:y,handleNativeElScroll:j,cssVars:i?void 0:I,themeClass:m==null?void 0:m.themeClass,onRender:m==null?void 0:m.onRender},R)},render(){var o;const{mergedClsPrefix:r,hasSider:u}=this;(o=this.onRender)===null||o===void 0||o.call(this);const b=u?this.hasSiderStyle:void 0,i=[this.themeClass,e&&`${r}-layout-content`,`${r}-layout`,`${r}-layout--${this.position}-positioned`];return d("div",{class:i,style:this.cssVars},this.nativeScrollbar?d("div",{ref:"scrollableElRef",class:[`${r}-layout-scroll-container`,this.contentClass],style:[this.contentStyle,b],onScroll:this.handleNativeElScroll},this.$slots):d(A,Object.assign({},this.scrollbarProps,{onScroll:this.onScroll,ref:"scrollbarInstRef",theme:this.mergedTheme.peers.Scrollbar,themeOverrides:this.mergedTheme.peerOverrides.Scrollbar,contentClass:this.contentClass,contentStyle:[this.contentStyle,b]}),this.$slots))}})}const Te=K(!1),_e=K(!0),ue=a("layout-sider",`
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
`,[p("bordered",[n("border",`
 content: "";
 position: absolute;
 top: 0;
 bottom: 0;
 width: 1px;
 background-color: var(--n-border-color);
 transition: background-color .3s var(--n-bezier);
 `)]),n("left-placement",[p("bordered",[n("border",`
 right: 0;
 `)])]),p("right-placement",`
 justify-content: flex-start;
 `,[p("bordered",[n("border",`
 left: 0;
 `)]),p("collapsed",[a("layout-toggle-button",[a("base-icon",`
 transform: rotate(180deg);
 `)]),a("layout-toggle-bar",[B("&:hover",[n("top",{transform:"rotate(-12deg) scale(1.15) translateY(-2px)"}),n("bottom",{transform:"rotate(12deg) scale(1.15) translateY(2px)"})])])]),a("layout-toggle-button",`
 left: 0;
 transform: translateX(-50%) translateY(-50%);
 `,[a("base-icon",`
 transform: rotate(0);
 `)]),a("layout-toggle-bar",`
 left: -28px;
 transform: rotate(180deg);
 `,[B("&:hover",[n("top",{transform:"rotate(12deg) scale(1.15) translateY(-2px)"}),n("bottom",{transform:"rotate(-12deg) scale(1.15) translateY(2px)"})])])]),p("collapsed",[a("layout-toggle-bar",[B("&:hover",[n("top",{transform:"rotate(-12deg) scale(1.15) translateY(-2px)"}),n("bottom",{transform:"rotate(12deg) scale(1.15) translateY(2px)"})])]),a("layout-toggle-button",[a("base-icon",`
 transform: rotate(0);
 `)])]),a("layout-toggle-button",`
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
 `,[a("base-icon",`
 transition: transform .3s var(--n-bezier);
 transform: rotate(180deg);
 `)]),a("layout-toggle-bar",`
 cursor: pointer;
 height: 72px;
 width: 32px;
 position: absolute;
 top: calc(50% - 36px);
 right: -28px;
 `,[n("top, bottom",`
 position: absolute;
 width: 4px;
 border-radius: 2px;
 height: 38px;
 left: 14px;
 transition: 
 background-color .3s var(--n-bezier),
 transform .3s var(--n-bezier);
 `),n("bottom",`
 position: absolute;
 top: 34px;
 `),B("&:hover",[n("top",{transform:"rotate(12deg) scale(1.15) translateY(-2px)"}),n("bottom",{transform:"rotate(-12deg) scale(1.15) translateY(2px)"})]),n("top, bottom",{backgroundColor:"var(--n-toggle-bar-color)"}),B("&:hover",[n("top, bottom",{backgroundColor:"var(--n-toggle-bar-color-hover)"})])]),n("border",`
 position: absolute;
 top: 0;
 right: 0;
 bottom: 0;
 width: 1px;
 transition: background-color .3s var(--n-bezier);
 `),a("layout-sider-scroll-container",`
 flex-grow: 1;
 flex-shrink: 0;
 box-sizing: border-box;
 height: 100%;
 opacity: 0;
 transition: opacity .3s var(--n-bezier);
 max-width: 100%;
 `),p("show-content",[a("layout-sider-scroll-container",{opacity:1})]),p("absolute-positioned",`
 position: absolute;
 left: 0;
 top: 0;
 bottom: 0;
 `)]),ge=w({props:{clsPrefix:{type:String,required:!0},onClick:Function},render(){const{clsPrefix:e}=this;return d("div",{onClick:this.onClick,class:`${e}-layout-toggle-bar`},d("div",{class:`${e}-layout-toggle-bar__top`}),d("div",{class:`${e}-layout-toggle-bar__bottom`}))}}),be=w({name:"LayoutToggleButton",props:{clsPrefix:{type:String,required:!0},onClick:Function},render(){const{clsPrefix:e}=this;return d("div",{class:`${e}-layout-toggle-button`,onClick:this.onClick},d(oe,{clsPrefix:e},{default:()=>d(se,null)}))}}),he={position:X,bordered:Boolean,collapsedWidth:{type:Number,default:48},width:{type:[Number,String],default:272},contentClass:String,contentStyle:{type:[String,Object],default:""},collapseMode:{type:String,default:"transform"},collapsed:{type:Boolean,default:void 0},defaultCollapsed:Boolean,showCollapsedContent:{type:Boolean,default:!0},showTrigger:{type:[Boolean,String],default:!1},nativeScrollbar:{type:Boolean,default:!0},inverted:Boolean,scrollbarProps:Object,triggerClass:String,triggerStyle:[String,Object],collapsedTriggerClass:String,collapsedTriggerStyle:[String,Object],"onUpdate:collapsed":[Function,Array],onUpdateCollapsed:[Function,Array],onAfterEnter:Function,onAfterLeave:Function,onExpand:[Function,Array],onCollapse:[Function,Array],onScroll:Function},Be=w({name:"LayoutSider",props:Object.assign(Object.assign({},O.props),he),setup(e){const o=te(q),r=k(null),u=k(null),b=k(e.defaultCollapsed),i=ne(Y(e,"collapsed"),b),y=C(()=>E(i.value?e.collapsedWidth:e.width)),_=C(()=>e.collapseMode!=="transform"?{}:{minWidth:E(e.width)}),x=C(()=>o?o.siderPlacement:"left");function h(s,t){if(e.nativeScrollbar){const{value:l}=r;l&&(t===void 0?l.scrollTo(s):l.scrollTo(s,t))}else{const{value:l}=u;l&&l.scrollTo(s,t)}}function j(){const{"onUpdate:collapsed":s,onUpdateCollapsed:t,onExpand:l,onCollapse:P}=e,{value:T}=i;t&&$(t,!T),s&&$(s,!T),b.value=!T,T?l&&$(l):P&&$(P)}let z=0,R=0;const I=s=>{var t;const l=s.target;z=l.scrollLeft,R=l.scrollTop,(t=e.onScroll)===null||t===void 0||t.call(e,s)};V(()=>{if(e.nativeScrollbar){const s=r.value;s&&(s.scrollTop=R,s.scrollLeft=z)}}),U(ie,{collapsedRef:i,collapseModeRef:Y(e,"collapseMode")});const{mergedClsPrefixRef:m,inlineThemeDisabled:c}=W(e),g=O("Layout","-layout-sider",ue,D,e,m);function f(s){var t,l;s.propertyName==="max-width"&&(i.value?(t=e.onAfterLeave)===null||t===void 0||t.call(e):(l=e.onAfterEnter)===null||l===void 0||l.call(e))}const G={scrollTo:h},M=C(()=>{const{common:{cubicBezierEaseInOut:s},self:t}=g.value,{siderToggleButtonColor:l,siderToggleButtonBorder:P,siderToggleBarColor:T,siderToggleBarColorHover:J}=t,v={"--n-bezier":s,"--n-toggle-button-color":l,"--n-toggle-button-border":P,"--n-toggle-bar-color":T,"--n-toggle-bar-color-hover":J};return e.inverted?(v["--n-color"]=t.siderColorInverted,v["--n-text-color"]=t.textColorInverted,v["--n-border-color"]=t.siderBorderColorInverted,v["--n-toggle-button-icon-color"]=t.siderToggleButtonIconColorInverted,v.__invertScrollbar=t.__invertScrollbar):(v["--n-color"]=t.siderColor,v["--n-text-color"]=t.textColor,v["--n-border-color"]=t.siderBorderColor,v["--n-toggle-button-icon-color"]=t.siderToggleButtonIconColor),v}),S=c?H("layout-sider",C(()=>e.inverted?"a":"b"),M,e):void 0;return Object.assign({scrollableElRef:r,scrollbarInstRef:u,mergedClsPrefix:m,mergedTheme:g,styleMaxWidth:y,mergedCollapsed:i,scrollContainerStyle:_,siderPlacement:x,handleNativeElScroll:I,handleTransitionend:f,handleTriggerClick:j,inlineThemeDisabled:c,cssVars:M,themeClass:S==null?void 0:S.themeClass,onRender:S==null?void 0:S.onRender},G)},render(){var e;const{mergedClsPrefix:o,mergedCollapsed:r,showTrigger:u}=this;return(e=this.onRender)===null||e===void 0||e.call(this),d("aside",{class:[`${o}-layout-sider`,this.themeClass,`${o}-layout-sider--${this.position}-positioned`,`${o}-layout-sider--${this.siderPlacement}-placement`,this.bordered&&`${o}-layout-sider--bordered`,r&&`${o}-layout-sider--collapsed`,(!r||this.showCollapsedContent)&&`${o}-layout-sider--show-content`],onTransitionend:this.handleTransitionend,style:[this.inlineThemeDisabled?void 0:this.cssVars,{maxWidth:this.styleMaxWidth,width:E(this.width)}]},this.nativeScrollbar?d("div",{class:[`${o}-layout-sider-scroll-container`,this.contentClass],onScroll:this.handleNativeElScroll,style:[this.scrollContainerStyle,{overflow:"auto"},this.contentStyle],ref:"scrollableElRef"},this.$slots):d(A,Object.assign({},this.scrollbarProps,{onScroll:this.onScroll,ref:"scrollbarInstRef",style:this.scrollContainerStyle,contentStyle:this.contentStyle,contentClass:this.contentClass,theme:this.mergedTheme.peers.Scrollbar,themeOverrides:this.mergedTheme.peerOverrides.Scrollbar,builtinThemeOverrides:this.inverted&&this.cssVars.__invertScrollbar==="true"?{colorHover:"rgba(255, 255, 255, .4)",color:"rgba(255, 255, 255, .3)"}:void 0}),this.$slots),u?u==="bar"?d(ge,{clsPrefix:o,class:r?this.collapsedTriggerClass:this.triggerClass,style:r?this.collapsedTriggerStyle:this.triggerStyle,onClick:this.handleTriggerClick}):d(be,{clsPrefix:o,class:r?this.collapsedTriggerClass:this.triggerClass,style:r?this.collapsedTriggerStyle:this.triggerStyle,onClick:this.handleTriggerClick}):null,this.bordered?d("div",{class:`${o}-layout-sider__border`}):null)}}),fe={xmlns:"http://www.w3.org/2000/svg","xmlns:xlink":"http://www.w3.org/1999/xlink",viewBox:"0 0 512 512"},ve=L("path",{fill:"none",stroke:"currentColor","stroke-linecap":"round","stroke-miterlimit":"10","stroke-width":"32",d:"M80 160h352"},null,-1),me=L("path",{fill:"none",stroke:"currentColor","stroke-linecap":"round","stroke-miterlimit":"10","stroke-width":"32",d:"M80 256h352"},null,-1),pe=L("path",{fill:"none",stroke:"currentColor","stroke-linecap":"round","stroke-miterlimit":"10","stroke-width":"32",d:"M80 352h352"},null,-1),ye=[ve,me,pe],ke=w({name:"MenuOutline",render:function(o,r){return re(),le("svg",fe,ye)}});export{ke as M,Te as _,ie as a,Be as b,_e as c,D as l,X as p};
