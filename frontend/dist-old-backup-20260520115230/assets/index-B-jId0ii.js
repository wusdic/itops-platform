import{j as O,k as p,l as Le,m as b,n as x,p as R,q as C,s as _e,v as Q,x as He,y,z as ce,A as te,C as xe,i as M,o as Fe,D as ye,E as Ye,F as K,G as We,H as eo,I as pe,J as ee,K as oo,L as Z,N as to,M as ke,O as ze,P as Ke,Q as fe,R as ro,V as no,S as Ne,T as io,U as lo,W as G,e as X,c as ae,a as B,u as ao,X as co,Y as Te,w as _,d as so,Z as uo,_ as vo,b as I,B as mo,f as ie,h as ge,t as oe,$ as ho,a0 as po,a1 as fo,a2 as go,a3 as bo,a4 as Co}from"./index-DKN09kKZ.js";import{r as k}from"./request-POaVrfAG.js";import{_ as xo}from"./_plugin-vue_export-helper-DlAUqK2U.js";import{u as yo}from"./composables--wRKVNEC.js";import{l as zo,p as Io,a as wo,_ as _o,M as Ho,b as ko,c as Ao}from"./MenuOutline-Bnf3gYqv.js";import{_ as Ro}from"./Space-ZsUS5rjF.js";import{N as So}from"./Badge-34XJXOn2.js";import{d as Po,_ as je}from"./Dropdown-zohXMmt3.js";import{N as No}from"./Avatar-D2-hQ12u.js";import{S as $e}from"./ServerOutline-_vDienKc.js";import{t as To,_ as $o}from"./Tooltip-BN--rdLs.js";import{u as Oe}from"./get-KUEEAmRn.js";import{V as Oo,c as be}from"./create-J4QfWyXQ.js";import{u as Eo}from"./Popover-DGWfQEMx.js";import{G as Mo,F as Bo,S as Lo}from"./SettingsOutline-to5u25OR.js";import{T as Fo}from"./TicketOutline-BP57gTA5.js";import{B as Ko,S as jo}from"./SparklesOutline-CHKySv5W.js";import{N as Vo}from"./Icon-3H3pIWQR.js";import"./ChevronRight-DcBQWbXd.js";import"./happens-in-CM8LO42l.js";import"./use-keyboard-CDrGd5wN.js";import"./create-ref-setter-C4J8sofl.js";const Do=O({name:"ChevronDownFilled",render(){return p("svg",{viewBox:"0 0 16 16",fill:"none",xmlns:"http://www.w3.org/2000/svg"},p("path",{d:"M3.20041 5.73966C3.48226 5.43613 3.95681 5.41856 4.26034 5.70041L8 9.22652L11.7397 5.70041C12.0432 5.41856 12.5177 5.43613 12.7996 5.73966C13.0815 6.0432 13.0639 6.51775 12.7603 6.7996L8.51034 10.7996C8.22258 11.0668 7.77743 11.0668 7.48967 10.7996L3.23966 6.7996C2.93613 6.51775 2.91856 6.0432 3.20041 5.73966Z",fill:"currentColor"}))}}),Uo={fontWeightActive:"400"};function Go(e){const{fontSize:r,textColor3:o,textColor2:n,borderRadius:a,buttonColor2Hover:l,buttonColor2Pressed:s}=e;return Object.assign(Object.assign({},Uo),{fontSize:r,itemLineHeight:"1.25",itemTextColor:o,itemTextColorHover:n,itemTextColorPressed:n,itemTextColorActive:n,itemBorderRadius:a,itemColorHover:l,itemColorPressed:s,separatorColor:o})}const qo={common:Le,self:Go},Jo=b("breadcrumb",`
 white-space: nowrap;
 cursor: default;
 line-height: var(--n-item-line-height);
`,[x("ul",`
 list-style: none;
 padding: 0;
 margin: 0;
 `),x("a",`
 color: inherit;
 text-decoration: inherit;
 `),b("breadcrumb-item",`
 font-size: var(--n-font-size);
 transition: color .3s var(--n-bezier);
 display: inline-flex;
 align-items: center;
 `,[b("icon",`
 font-size: 18px;
 vertical-align: -.2em;
 transition: color .3s var(--n-bezier);
 color: var(--n-item-text-color);
 `),x("&:not(:last-child)",[R("clickable",[C("link",`
 cursor: pointer;
 `,[x("&:hover",`
 background-color: var(--n-item-color-hover);
 `),x("&:active",`
 background-color: var(--n-item-color-pressed); 
 `)])])]),C("link",`
 padding: 4px;
 border-radius: var(--n-item-border-radius);
 transition:
 background-color .3s var(--n-bezier),
 color .3s var(--n-bezier);
 color: var(--n-item-text-color);
 position: relative;
 `,[x("&:hover",`
 color: var(--n-item-text-color-hover);
 `,[b("icon",`
 color: var(--n-item-text-color-hover);
 `)]),x("&:active",`
 color: var(--n-item-text-color-pressed);
 `,[b("icon",`
 color: var(--n-item-text-color-pressed);
 `)])]),C("separator",`
 margin: 0 8px;
 color: var(--n-separator-color);
 transition: color .3s var(--n-bezier);
 user-select: none;
 -webkit-user-select: none;
 `),x("&:last-child",[C("link",`
 font-weight: var(--n-font-weight-active);
 cursor: unset;
 color: var(--n-item-text-color-active);
 `,[b("icon",`
 color: var(--n-item-text-color-active);
 `)]),C("separator",`
 display: none;
 `)])])]),Ve=ce("n-breadcrumb"),Xo=Object.assign(Object.assign({},Q.props),{separator:{type:String,default:"/"}}),Zo=O({name:"Breadcrumb",props:Xo,setup(e){const{mergedClsPrefixRef:r,inlineThemeDisabled:o}=_e(e),n=Q("Breadcrumb","-breadcrumb",Jo,qo,e,r);te(Ve,{separatorRef:xe(e,"separator"),mergedClsPrefixRef:r});const a=y(()=>{const{common:{cubicBezierEaseInOut:s},self:{separatorColor:u,itemTextColor:c,itemTextColorHover:f,itemTextColorPressed:A,itemTextColorActive:w,fontSize:v,fontWeightActive:S,itemBorderRadius:N,itemColorHover:P,itemColorPressed:T,itemLineHeight:$}}=n.value;return{"--n-font-size":v,"--n-bezier":s,"--n-item-text-color":c,"--n-item-text-color-hover":f,"--n-item-text-color-pressed":A,"--n-item-text-color-active":w,"--n-separator-color":u,"--n-item-color-hover":P,"--n-item-color-pressed":T,"--n-item-border-radius":N,"--n-font-weight-active":S,"--n-item-line-height":$}}),l=o?He("breadcrumb",void 0,a,e):void 0;return{mergedClsPrefix:r,cssVars:o?void 0:a,themeClass:l==null?void 0:l.themeClass,onRender:l==null?void 0:l.onRender}},render(){var e;return(e=this.onRender)===null||e===void 0||e.call(this),p("nav",{class:[`${this.mergedClsPrefix}-breadcrumb`,this.themeClass],style:this.cssVars,"aria-label":"Breadcrumb"},p("ul",null,this.$slots))}});function Qo(e=Ye?window:null){const r=()=>{const{hash:a,host:l,hostname:s,href:u,origin:c,pathname:f,port:A,protocol:w,search:v}=(e==null?void 0:e.location)||{};return{hash:a,host:l,hostname:s,href:u,origin:c,pathname:f,port:A,protocol:w,search:v}},o=M(r()),n=()=>{o.value=r()};return Fe(()=>{e&&(e.addEventListener("popstate",n),e.addEventListener("hashchange",n))}),ye(()=>{e&&(e.removeEventListener("popstate",n),e.removeEventListener("hashchange",n))}),o}const Yo={separator:String,href:String,clickable:{type:Boolean,default:!0},onClick:Function},Wo=O({name:"BreadcrumbItem",props:Yo,slots:Object,setup(e,{slots:r}){const o=K(Ve,null);if(!o)return()=>null;const{separatorRef:n,mergedClsPrefixRef:a}=o,l=Qo(),s=y(()=>e.href?"a":"span"),u=y(()=>l.value.href===e.href?"location":null);return()=>{const{value:c}=a;return p("li",{class:[`${c}-breadcrumb-item`,e.clickable&&`${c}-breadcrumb-item--clickable`]},p(s.value,{class:`${c}-breadcrumb-item__link`,"aria-current":u.value,href:e.href,onClick:e.onClick},r),p("span",{class:`${c}-breadcrumb-item__separator`,"aria-hidden":"true"},We(r.separator,()=>{var f;return[(f=e.separator)!==null&&f!==void 0?f:n.value]})))}}});function et(e,r,o,n){return{itemColorHoverInverted:"#0000",itemColorActiveInverted:r,itemColorActiveHoverInverted:r,itemColorActiveCollapsedInverted:r,itemTextColorInverted:e,itemTextColorHoverInverted:o,itemTextColorChildActiveInverted:o,itemTextColorChildActiveHoverInverted:o,itemTextColorActiveInverted:o,itemTextColorActiveHoverInverted:o,itemTextColorHorizontalInverted:e,itemTextColorHoverHorizontalInverted:o,itemTextColorChildActiveHorizontalInverted:o,itemTextColorChildActiveHoverHorizontalInverted:o,itemTextColorActiveHorizontalInverted:o,itemTextColorActiveHoverHorizontalInverted:o,itemIconColorInverted:e,itemIconColorHoverInverted:o,itemIconColorActiveInverted:o,itemIconColorActiveHoverInverted:o,itemIconColorChildActiveInverted:o,itemIconColorChildActiveHoverInverted:o,itemIconColorCollapsedInverted:e,itemIconColorHorizontalInverted:e,itemIconColorHoverHorizontalInverted:o,itemIconColorActiveHorizontalInverted:o,itemIconColorActiveHoverHorizontalInverted:o,itemIconColorChildActiveHorizontalInverted:o,itemIconColorChildActiveHoverHorizontalInverted:o,arrowColorInverted:e,arrowColorHoverInverted:o,arrowColorActiveInverted:o,arrowColorActiveHoverInverted:o,arrowColorChildActiveInverted:o,arrowColorChildActiveHoverInverted:o,groupTextColorInverted:n}}function ot(e){const{borderRadius:r,textColor3:o,primaryColor:n,textColor2:a,textColor1:l,fontSize:s,dividerColor:u,hoverColor:c,primaryColorHover:f}=e;return Object.assign({borderRadius:r,color:"#0000",groupTextColor:o,itemColorHover:c,itemColorActive:pe(n,{alpha:.1}),itemColorActiveHover:pe(n,{alpha:.1}),itemColorActiveCollapsed:pe(n,{alpha:.1}),itemTextColor:a,itemTextColorHover:a,itemTextColorActive:n,itemTextColorActiveHover:n,itemTextColorChildActive:n,itemTextColorChildActiveHover:n,itemTextColorHorizontal:a,itemTextColorHoverHorizontal:f,itemTextColorActiveHorizontal:n,itemTextColorActiveHoverHorizontal:n,itemTextColorChildActiveHorizontal:n,itemTextColorChildActiveHoverHorizontal:n,itemIconColor:l,itemIconColorHover:l,itemIconColorActive:n,itemIconColorActiveHover:n,itemIconColorChildActive:n,itemIconColorChildActiveHover:n,itemIconColorCollapsed:l,itemIconColorHorizontal:l,itemIconColorHoverHorizontal:f,itemIconColorActiveHorizontal:n,itemIconColorActiveHoverHorizontal:n,itemIconColorChildActiveHorizontal:n,itemIconColorChildActiveHoverHorizontal:n,itemHeight:"42px",arrowColor:a,arrowColorHover:a,arrowColorActive:n,arrowColorActiveHover:n,arrowColorChildActive:n,arrowColorChildActiveHover:n,colorInverted:"#0000",borderColorHorizontal:"#0000",fontSize:s,dividerColor:u},et("#BBB",n,"#FFF","#AAA"))}const tt=eo({name:"Menu",common:Le,peers:{Tooltip:To,Dropdown:Po},self:ot}),rt=b("layout-header",`
 transition:
 color .3s var(--n-bezier),
 background-color .3s var(--n-bezier),
 box-shadow .3s var(--n-bezier),
 border-color .3s var(--n-bezier);
 box-sizing: border-box;
 width: 100%;
 background-color: var(--n-color);
 color: var(--n-text-color);
`,[R("absolute-positioned",`
 position: absolute;
 left: 0;
 right: 0;
 top: 0;
 `),R("bordered",`
 border-bottom: solid 1px var(--n-border-color);
 `)]),nt={position:Io,inverted:Boolean,bordered:{type:Boolean,default:!1}},it=O({name:"LayoutHeader",props:Object.assign(Object.assign({},Q.props),nt),setup(e){const{mergedClsPrefixRef:r,inlineThemeDisabled:o}=_e(e),n=Q("Layout","-layout-header",rt,zo,e,r),a=y(()=>{const{common:{cubicBezierEaseInOut:s},self:u}=n.value,c={"--n-bezier":s};return e.inverted?(c["--n-color"]=u.headerColorInverted,c["--n-text-color"]=u.textColorInverted,c["--n-border-color"]=u.headerBorderColorInverted):(c["--n-color"]=u.headerColor,c["--n-text-color"]=u.textColor,c["--n-border-color"]=u.headerBorderColor),c}),l=o?He("layout-header",y(()=>e.inverted?"a":"b"),a,e):void 0;return{mergedClsPrefix:r,cssVars:o?void 0:a,themeClass:l==null?void 0:l.themeClass,onRender:l==null?void 0:l.onRender}},render(){var e;const{mergedClsPrefix:r}=this;return(e=this.onRender)===null||e===void 0||e.call(this),p("div",{class:[`${r}-layout-header`,this.themeClass,this.position&&`${r}-layout-header--${this.position}-positioned`,this.bordered&&`${r}-layout-header--bordered`],style:this.cssVars},this.$slots)}}),re=ce("n-menu"),De=ce("n-submenu"),Ae=ce("n-menu-item-group"),Ee=[x("&::before","background-color: var(--n-item-color-hover);"),C("arrow",`
 color: var(--n-arrow-color-hover);
 `),C("icon",`
 color: var(--n-item-icon-color-hover);
 `),b("menu-item-content-header",`
 color: var(--n-item-text-color-hover);
 `,[x("a",`
 color: var(--n-item-text-color-hover);
 `),C("extra",`
 color: var(--n-item-text-color-hover);
 `)])],Me=[C("icon",`
 color: var(--n-item-icon-color-hover-horizontal);
 `),b("menu-item-content-header",`
 color: var(--n-item-text-color-hover-horizontal);
 `,[x("a",`
 color: var(--n-item-text-color-hover-horizontal);
 `),C("extra",`
 color: var(--n-item-text-color-hover-horizontal);
 `)])],lt=x([b("menu",`
 background-color: var(--n-color);
 color: var(--n-item-text-color);
 overflow: hidden;
 transition: background-color .3s var(--n-bezier);
 box-sizing: border-box;
 font-size: var(--n-font-size);
 padding-bottom: 6px;
 `,[R("horizontal",`
 max-width: 100%;
 width: 100%;
 display: flex;
 overflow: hidden;
 padding-bottom: 0;
 `,[b("submenu","margin: 0;"),b("menu-item","margin: 0;"),b("menu-item-content",`
 padding: 0 20px;
 border-bottom: 2px solid #0000;
 `,[x("&::before","display: none;"),R("selected","border-bottom: 2px solid var(--n-border-color-horizontal)")]),b("menu-item-content",[R("selected",[C("icon","color: var(--n-item-icon-color-active-horizontal);"),b("menu-item-content-header",`
 color: var(--n-item-text-color-active-horizontal);
 `,[x("a","color: var(--n-item-text-color-active-horizontal);"),C("extra","color: var(--n-item-text-color-active-horizontal);")])]),R("child-active",`
 border-bottom: 2px solid var(--n-border-color-horizontal);
 `,[b("menu-item-content-header",`
 color: var(--n-item-text-color-child-active-horizontal);
 `,[x("a",`
 color: var(--n-item-text-color-child-active-horizontal);
 `),C("extra",`
 color: var(--n-item-text-color-child-active-horizontal);
 `)]),C("icon",`
 color: var(--n-item-icon-color-child-active-horizontal);
 `)]),ee("disabled",[ee("selected, child-active",[x("&:focus-within",Me)]),R("selected",[q(null,[C("icon","color: var(--n-item-icon-color-active-hover-horizontal);"),b("menu-item-content-header",`
 color: var(--n-item-text-color-active-hover-horizontal);
 `,[x("a","color: var(--n-item-text-color-active-hover-horizontal);"),C("extra","color: var(--n-item-text-color-active-hover-horizontal);")])])]),R("child-active",[q(null,[C("icon","color: var(--n-item-icon-color-child-active-hover-horizontal);"),b("menu-item-content-header",`
 color: var(--n-item-text-color-child-active-hover-horizontal);
 `,[x("a","color: var(--n-item-text-color-child-active-hover-horizontal);"),C("extra","color: var(--n-item-text-color-child-active-hover-horizontal);")])])]),q("border-bottom: 2px solid var(--n-border-color-horizontal);",Me)]),b("menu-item-content-header",[x("a","color: var(--n-item-text-color-horizontal);")])])]),ee("responsive",[b("menu-item-content-header",`
 overflow: hidden;
 text-overflow: ellipsis;
 `)]),R("collapsed",[b("menu-item-content",[R("selected",[x("&::before",`
 background-color: var(--n-item-color-active-collapsed) !important;
 `)]),b("menu-item-content-header","opacity: 0;"),C("arrow","opacity: 0;"),C("icon","color: var(--n-item-icon-color-collapsed);")])]),b("menu-item",`
 height: var(--n-item-height);
 margin-top: 6px;
 position: relative;
 `),b("menu-item-content",`
 box-sizing: border-box;
 line-height: 1.75;
 height: 100%;
 display: grid;
 grid-template-areas: "icon content arrow";
 grid-template-columns: auto 1fr auto;
 align-items: center;
 cursor: pointer;
 position: relative;
 padding-right: 18px;
 transition:
 background-color .3s var(--n-bezier),
 padding-left .3s var(--n-bezier),
 border-color .3s var(--n-bezier);
 `,[x("> *","z-index: 1;"),x("&::before",`
 z-index: auto;
 content: "";
 background-color: #0000;
 position: absolute;
 left: 8px;
 right: 8px;
 top: 0;
 bottom: 0;
 pointer-events: none;
 border-radius: var(--n-border-radius);
 transition: background-color .3s var(--n-bezier);
 `),R("disabled",`
 opacity: .45;
 cursor: not-allowed;
 `),R("collapsed",[C("arrow","transform: rotate(0);")]),R("selected",[x("&::before","background-color: var(--n-item-color-active);"),C("arrow","color: var(--n-arrow-color-active);"),C("icon","color: var(--n-item-icon-color-active);"),b("menu-item-content-header",`
 color: var(--n-item-text-color-active);
 `,[x("a","color: var(--n-item-text-color-active);"),C("extra","color: var(--n-item-text-color-active);")])]),R("child-active",[b("menu-item-content-header",`
 color: var(--n-item-text-color-child-active);
 `,[x("a",`
 color: var(--n-item-text-color-child-active);
 `),C("extra",`
 color: var(--n-item-text-color-child-active);
 `)]),C("arrow",`
 color: var(--n-arrow-color-child-active);
 `),C("icon",`
 color: var(--n-item-icon-color-child-active);
 `)]),ee("disabled",[ee("selected, child-active",[x("&:focus-within",Ee)]),R("selected",[q(null,[C("arrow","color: var(--n-arrow-color-active-hover);"),C("icon","color: var(--n-item-icon-color-active-hover);"),b("menu-item-content-header",`
 color: var(--n-item-text-color-active-hover);
 `,[x("a","color: var(--n-item-text-color-active-hover);"),C("extra","color: var(--n-item-text-color-active-hover);")])])]),R("child-active",[q(null,[C("arrow","color: var(--n-arrow-color-child-active-hover);"),C("icon","color: var(--n-item-icon-color-child-active-hover);"),b("menu-item-content-header",`
 color: var(--n-item-text-color-child-active-hover);
 `,[x("a","color: var(--n-item-text-color-child-active-hover);"),C("extra","color: var(--n-item-text-color-child-active-hover);")])])]),R("selected",[q(null,[x("&::before","background-color: var(--n-item-color-active-hover);")])]),q(null,Ee)]),C("icon",`
 grid-area: icon;
 color: var(--n-item-icon-color);
 transition:
 color .3s var(--n-bezier),
 font-size .3s var(--n-bezier),
 margin-right .3s var(--n-bezier);
 box-sizing: content-box;
 display: inline-flex;
 align-items: center;
 justify-content: center;
 `),C("arrow",`
 grid-area: arrow;
 font-size: 16px;
 color: var(--n-arrow-color);
 transform: rotate(180deg);
 opacity: 1;
 transition:
 color .3s var(--n-bezier),
 transform 0.2s var(--n-bezier),
 opacity 0.2s var(--n-bezier);
 `),b("menu-item-content-header",`
 grid-area: content;
 transition:
 color .3s var(--n-bezier),
 opacity .3s var(--n-bezier);
 opacity: 1;
 white-space: nowrap;
 color: var(--n-item-text-color);
 `,[x("a",`
 outline: none;
 text-decoration: none;
 transition: color .3s var(--n-bezier);
 color: var(--n-item-text-color);
 `,[x("&::before",`
 content: "";
 position: absolute;
 left: 0;
 right: 0;
 top: 0;
 bottom: 0;
 `)]),C("extra",`
 font-size: .93em;
 color: var(--n-group-text-color);
 transition: color .3s var(--n-bezier);
 `)])]),b("submenu",`
 cursor: pointer;
 position: relative;
 margin-top: 6px;
 `,[b("menu-item-content",`
 height: var(--n-item-height);
 `),b("submenu-children",`
 overflow: hidden;
 padding: 0;
 `,[oo({duration:".2s"})])]),b("menu-item-group",[b("menu-item-group-title",`
 margin-top: 6px;
 color: var(--n-group-text-color);
 cursor: default;
 font-size: .93em;
 height: 36px;
 display: flex;
 align-items: center;
 transition:
 padding-left .3s var(--n-bezier),
 color .3s var(--n-bezier);
 `)])]),b("menu-tooltip",[x("a",`
 color: inherit;
 text-decoration: none;
 `)]),b("menu-divider",`
 transition: background-color .3s var(--n-bezier);
 background-color: var(--n-divider-color);
 height: 1px;
 margin: 6px 18px;
 `)]);function q(e,r){return[R("hover",e,r),x("&:hover",e,r)]}const Ue=O({name:"MenuOptionContent",props:{collapsed:Boolean,disabled:Boolean,title:[String,Function],icon:Function,extra:[String,Function],showArrow:Boolean,childActive:Boolean,hover:Boolean,paddingLeft:Number,selected:Boolean,maxIconSize:{type:Number,required:!0},activeIconSize:{type:Number,required:!0},iconMarginRight:{type:Number,required:!0},clsPrefix:{type:String,required:!0},onClick:Function,tmNode:{type:Object,required:!0},isEllipsisPlaceholder:Boolean},setup(e){const{props:r}=K(re);return{menuProps:r,style:y(()=>{const{paddingLeft:o}=e;return{paddingLeft:o&&`${o}px`}}),iconStyle:y(()=>{const{maxIconSize:o,activeIconSize:n,iconMarginRight:a}=e;return{width:`${o}px`,height:`${o}px`,fontSize:`${n}px`,marginRight:`${a}px`}})}},render(){const{clsPrefix:e,tmNode:r,menuProps:{renderIcon:o,renderLabel:n,renderExtra:a,expandIcon:l}}=this,s=o?o(r.rawNode):Z(this.icon);return p("div",{onClick:u=>{var c;(c=this.onClick)===null||c===void 0||c.call(this,u)},role:"none",class:[`${e}-menu-item-content`,{[`${e}-menu-item-content--selected`]:this.selected,[`${e}-menu-item-content--collapsed`]:this.collapsed,[`${e}-menu-item-content--child-active`]:this.childActive,[`${e}-menu-item-content--disabled`]:this.disabled,[`${e}-menu-item-content--hover`]:this.hover}],style:this.style},s&&p("div",{class:`${e}-menu-item-content__icon`,style:this.iconStyle,role:"none"},[s]),p("div",{class:`${e}-menu-item-content-header`,role:"none"},this.isEllipsisPlaceholder?this.title:n?n(r.rawNode):Z(this.title),this.extra||a?p("span",{class:`${e}-menu-item-content-header__extra`}," ",a?a(r.rawNode):Z(this.extra)):null),this.showArrow?p(to,{ariaHidden:!0,class:`${e}-menu-item-content__arrow`,clsPrefix:e},{default:()=>l?l(r.rawNode):p(Do,null)}):null)}}),le=8;function Re(e){const r=K(re),{props:o,mergedCollapsedRef:n}=r,a=K(De,null),l=K(Ae,null),s=y(()=>o.mode==="horizontal"),u=y(()=>s.value?o.dropdownPlacement:"tmNodes"in e?"right-start":"right"),c=y(()=>{var v;return Math.max((v=o.collapsedIconSize)!==null&&v!==void 0?v:o.iconSize,o.iconSize)}),f=y(()=>{var v;return!s.value&&e.root&&n.value&&(v=o.collapsedIconSize)!==null&&v!==void 0?v:o.iconSize}),A=y(()=>{if(s.value)return;const{collapsedWidth:v,indent:S,rootIndent:N}=o,{root:P,isGroup:T}=e,$=N===void 0?S:N;return P?n.value?v/2-c.value/2:$:l&&typeof l.paddingLeftRef.value=="number"?S/2+l.paddingLeftRef.value:a&&typeof a.paddingLeftRef.value=="number"?(T?S/2:S)+a.paddingLeftRef.value:0}),w=y(()=>{const{collapsedWidth:v,indent:S,rootIndent:N}=o,{value:P}=c,{root:T}=e;return s.value||!T||!n.value?le:(N===void 0?S:N)+P+le-(v+P)/2});return{dropdownPlacement:u,activeIconSize:f,maxIconSize:c,paddingLeft:A,iconMarginRight:w,NMenu:r,NSubmenu:a,NMenuOptionGroup:l}}const Se={internalKey:{type:[String,Number],required:!0},root:Boolean,isGroup:Boolean,level:{type:Number,required:!0},title:[String,Function],extra:[String,Function]},at=O({name:"MenuDivider",setup(){const e=K(re),{mergedClsPrefixRef:r,isHorizontalRef:o}=e;return()=>o.value?null:p("div",{class:`${r.value}-menu-divider`})}}),Ge=Object.assign(Object.assign({},Se),{tmNode:{type:Object,required:!0},disabled:Boolean,icon:Function,onClick:Function}),ct=ke(Ge),st=O({name:"MenuOption",props:Ge,setup(e){const r=Re(e),{NSubmenu:o,NMenu:n,NMenuOptionGroup:a}=r,{props:l,mergedClsPrefixRef:s,mergedCollapsedRef:u}=n,c=o?o.mergedDisabledRef:a?a.mergedDisabledRef:{value:!1},f=y(()=>c.value||e.disabled);function A(v){const{onClick:S}=e;S&&S(v)}function w(v){f.value||(n.doSelect(e.internalKey,e.tmNode.rawNode),A(v))}return{mergedClsPrefix:s,dropdownPlacement:r.dropdownPlacement,paddingLeft:r.paddingLeft,iconMarginRight:r.iconMarginRight,maxIconSize:r.maxIconSize,activeIconSize:r.activeIconSize,mergedTheme:n.mergedThemeRef,menuProps:l,dropdownEnabled:ze(()=>e.root&&u.value&&l.mode!=="horizontal"&&!f.value),selected:ze(()=>n.mergedValueRef.value===e.internalKey),mergedDisabled:f,handleClick:w}},render(){const{mergedClsPrefix:e,mergedTheme:r,tmNode:o,menuProps:{renderLabel:n,nodeProps:a}}=this,l=a==null?void 0:a(o.rawNode);return p("div",Object.assign({},l,{role:"menuitem",class:[`${e}-menu-item`,l==null?void 0:l.class]}),p($o,{theme:r.peers.Tooltip,themeOverrides:r.peerOverrides.Tooltip,trigger:"hover",placement:this.dropdownPlacement,disabled:!this.dropdownEnabled||this.title===void 0,internalExtraClass:["menu-tooltip"]},{default:()=>n?n(o.rawNode):Z(this.title),trigger:()=>p(Ue,{tmNode:o,clsPrefix:e,paddingLeft:this.paddingLeft,iconMarginRight:this.iconMarginRight,maxIconSize:this.maxIconSize,activeIconSize:this.activeIconSize,selected:this.selected,title:this.title,extra:this.extra,disabled:this.mergedDisabled,icon:this.icon,onClick:this.handleClick})}))}}),qe=Object.assign(Object.assign({},Se),{tmNode:{type:Object,required:!0},tmNodes:{type:Array,required:!0}}),dt=ke(qe),ut=O({name:"MenuOptionGroup",props:qe,setup(e){const r=Re(e),{NSubmenu:o}=r,n=y(()=>o!=null&&o.mergedDisabledRef.value?!0:e.tmNode.disabled);te(Ae,{paddingLeftRef:r.paddingLeft,mergedDisabledRef:n});const{mergedClsPrefixRef:a,props:l}=K(re);return function(){const{value:s}=a,u=r.paddingLeft.value,{nodeProps:c}=l,f=c==null?void 0:c(e.tmNode.rawNode);return p("div",{class:`${s}-menu-item-group`,role:"group"},p("div",Object.assign({},f,{class:[`${s}-menu-item-group-title`,f==null?void 0:f.class],style:[(f==null?void 0:f.style)||"",u!==void 0?`padding-left: ${u}px;`:""]}),Z(e.title),e.extra?p(Ke,null," ",Z(e.extra)):null),p("div",null,e.tmNodes.map(A=>Pe(A,l))))}}});function Ie(e){return e.type==="divider"||e.type==="render"}function vt(e){return e.type==="divider"}function Pe(e,r){const{rawNode:o}=e,{show:n}=o;if(n===!1)return null;if(Ie(o))return vt(o)?p(at,Object.assign({key:e.key},o.props)):null;const{labelField:a}=r,{key:l,level:s,isGroup:u}=e,c=Object.assign(Object.assign({},o),{title:o.title||o[a],extra:o.titleExtra||o.extra,key:l,internalKey:l,level:s,root:s===0,isGroup:u});return e.children?e.isGroup?p(ut,fe(c,dt,{tmNode:e,tmNodes:e.children,key:l})):p(we,fe(c,mt,{key:l,rawNodes:o[r.childrenField],tmNodes:e.children,tmNode:e})):p(st,fe(c,ct,{key:l,tmNode:e}))}const Je=Object.assign(Object.assign({},Se),{rawNodes:{type:Array,default:()=>[]},tmNodes:{type:Array,default:()=>[]},tmNode:{type:Object,required:!0},disabled:Boolean,icon:Function,onClick:Function,domId:String,virtualChildActive:{type:Boolean,default:void 0},isEllipsisPlaceholder:Boolean}),mt=ke(Je),we=O({name:"Submenu",props:Je,setup(e){const r=Re(e),{NMenu:o,NSubmenu:n}=r,{props:a,mergedCollapsedRef:l,mergedThemeRef:s}=o,u=y(()=>{const{disabled:v}=e;return n!=null&&n.mergedDisabledRef.value||a.disabled?!0:v}),c=M(!1);te(De,{paddingLeftRef:r.paddingLeft,mergedDisabledRef:u}),te(Ae,null);function f(){const{onClick:v}=e;v&&v()}function A(){u.value||(l.value||o.toggleExpand(e.internalKey),f())}function w(v){c.value=v}return{menuProps:a,mergedTheme:s,doSelect:o.doSelect,inverted:o.invertedRef,isHorizontal:o.isHorizontalRef,mergedClsPrefix:o.mergedClsPrefixRef,maxIconSize:r.maxIconSize,activeIconSize:r.activeIconSize,iconMarginRight:r.iconMarginRight,dropdownPlacement:r.dropdownPlacement,dropdownShow:c,paddingLeft:r.paddingLeft,mergedDisabled:u,mergedValue:o.mergedValueRef,childActive:ze(()=>{var v;return(v=e.virtualChildActive)!==null&&v!==void 0?v:o.activePathRef.value.includes(e.internalKey)}),collapsed:y(()=>a.mode==="horizontal"?!1:l.value?!0:!o.mergedExpandedKeysRef.value.includes(e.internalKey)),dropdownEnabled:y(()=>!u.value&&(a.mode==="horizontal"||l.value)),handlePopoverShowChange:w,handleClick:A}},render(){var e;const{mergedClsPrefix:r,menuProps:{renderIcon:o,renderLabel:n}}=this,a=()=>{const{isHorizontal:s,paddingLeft:u,collapsed:c,mergedDisabled:f,maxIconSize:A,activeIconSize:w,title:v,childActive:S,icon:N,handleClick:P,menuProps:{nodeProps:T},dropdownShow:$,iconMarginRight:J,tmNode:L,mergedClsPrefix:j,isEllipsisPlaceholder:V,extra:h}=this,z=T==null?void 0:T(L.rawNode);return p("div",Object.assign({},z,{class:[`${j}-menu-item`,z==null?void 0:z.class],role:"menuitem"}),p(Ue,{tmNode:L,paddingLeft:u,collapsed:c,disabled:f,iconMarginRight:J,maxIconSize:A,activeIconSize:w,title:v,extra:h,showArrow:!s,childActive:S,clsPrefix:j,icon:N,hover:$,onClick:P,isEllipsisPlaceholder:V}))},l=()=>p(ro,null,{default:()=>{const{tmNodes:s,collapsed:u}=this;return u?null:p("div",{class:`${r}-submenu-children`,role:"menu"},s.map(c=>Pe(c,this.menuProps)))}});return this.root?p(je,Object.assign({size:"large",trigger:"hover"},(e=this.menuProps)===null||e===void 0?void 0:e.dropdownProps,{themeOverrides:this.mergedTheme.peerOverrides.Dropdown,theme:this.mergedTheme.peers.Dropdown,builtinThemeOverrides:{fontSizeLarge:"14px",optionIconSizeLarge:"18px"},value:this.mergedValue,disabled:!this.dropdownEnabled,placement:this.dropdownPlacement,keyField:this.menuProps.keyField,labelField:this.menuProps.labelField,childrenField:this.menuProps.childrenField,onUpdateShow:this.handlePopoverShowChange,options:this.rawNodes,onSelect:this.doSelect,inverted:this.inverted,renderIcon:o,renderLabel:n}),{default:()=>p("div",{class:`${r}-submenu`,role:"menu","aria-expanded":!this.collapsed,id:this.domId},a(),this.isHorizontal?null:l())}):p("div",{class:`${r}-submenu`,role:"menu","aria-expanded":!this.collapsed,id:this.domId},a(),l())}}),ht=Object.assign(Object.assign({},Q.props),{options:{type:Array,default:()=>[]},collapsed:{type:Boolean,default:void 0},collapsedWidth:{type:Number,default:48},iconSize:{type:Number,default:20},collapsedIconSize:{type:Number,default:24},rootIndent:Number,indent:{type:Number,default:32},labelField:{type:String,default:"label"},keyField:{type:String,default:"key"},childrenField:{type:String,default:"children"},disabledField:{type:String,default:"disabled"},defaultExpandAll:Boolean,defaultExpandedKeys:Array,expandedKeys:Array,value:[String,Number],defaultValue:{type:[String,Number],default:null},mode:{type:String,default:"vertical"},watchProps:{type:Array,default:void 0},disabled:Boolean,show:{type:Boolean,default:!0},inverted:Boolean,"onUpdate:expandedKeys":[Function,Array],onUpdateExpandedKeys:[Function,Array],onUpdateValue:[Function,Array],"onUpdate:value":[Function,Array],expandIcon:Function,renderIcon:Function,renderLabel:Function,renderExtra:Function,dropdownProps:Object,accordion:Boolean,nodeProps:Function,dropdownPlacement:{type:String,default:"bottom"},responsive:Boolean,items:Array,onOpenNamesChange:[Function,Array],onSelect:[Function,Array],onExpandedNamesChange:[Function,Array],expandedNames:Array,defaultExpandedNames:Array}),pt=O({name:"Menu",inheritAttrs:!1,props:ht,setup(e){const{mergedClsPrefixRef:r,inlineThemeDisabled:o}=_e(e),n=Q("Menu","-menu",lt,tt,e,r),a=K(wo,null),l=y(()=>{var d;const{collapsed:m}=e;if(m!==void 0)return m;if(a){const{collapseModeRef:t,collapsedRef:g}=a;if(t.value==="width")return(d=g.value)!==null&&d!==void 0?d:!1}return!1}),s=y(()=>{const{keyField:d,childrenField:m,disabledField:t}=e;return be(e.items||e.options,{getIgnored(g){return Ie(g)},getChildren(g){return g[m]},getDisabled(g){return g[t]},getKey(g){var H;return(H=g[d])!==null&&H!==void 0?H:g.name}})}),u=y(()=>new Set(s.value.treeNodes.map(d=>d.key))),{watchProps:c}=e,f=M(null);c!=null&&c.includes("defaultValue")?Ne(()=>{f.value=e.defaultValue}):f.value=e.defaultValue;const A=xe(e,"value"),w=Oe(A,f),v=M([]),S=()=>{v.value=e.defaultExpandAll?s.value.getNonLeafKeys():e.defaultExpandedNames||e.defaultExpandedKeys||s.value.getPath(w.value,{includeSelf:!1}).keyPath};c!=null&&c.includes("defaultExpandedKeys")?Ne(S):S();const N=Eo(e,["expandedNames","expandedKeys"]),P=Oe(N,v),T=y(()=>s.value.treeNodes),$=y(()=>s.value.getPath(w.value).keyPath);te(re,{props:e,mergedCollapsedRef:l,mergedThemeRef:n,mergedValueRef:w,mergedExpandedKeysRef:P,activePathRef:$,mergedClsPrefixRef:r,isHorizontalRef:y(()=>e.mode==="horizontal"),invertedRef:xe(e,"inverted"),doSelect:J,toggleExpand:j});function J(d,m){const{"onUpdate:value":t,onUpdateValue:g,onSelect:H}=e;g&&G(g,d,m),t&&G(t,d,m),H&&G(H,d,m),f.value=d}function L(d){const{"onUpdate:expandedKeys":m,onUpdateExpandedKeys:t,onExpandedNamesChange:g,onOpenNamesChange:H}=e;m&&G(m,d),t&&G(t,d),g&&G(g,d),H&&G(H,d),v.value=d}function j(d){const m=Array.from(P.value),t=m.findIndex(g=>g===d);if(~t)m.splice(t,1);else{if(e.accordion&&u.value.has(d)){const g=m.findIndex(H=>u.value.has(H));g>-1&&m.splice(g,1)}m.push(d)}L(m)}const V=d=>{const m=s.value.getPath(d??w.value,{includeSelf:!1}).keyPath;if(!m.length)return;const t=Array.from(P.value),g=new Set([...t,...m]);e.accordion&&u.value.forEach(H=>{g.has(H)&&!m.includes(H)&&g.delete(H)}),L(Array.from(g))},h=y(()=>{const{inverted:d}=e,{common:{cubicBezierEaseInOut:m},self:t}=n.value,{borderRadius:g,borderColorHorizontal:H,fontSize:Xe,itemHeight:Ze,dividerColor:Qe}=t,i={"--n-divider-color":Qe,"--n-bezier":m,"--n-font-size":Xe,"--n-border-color-horizontal":H,"--n-border-radius":g,"--n-item-height":Ze};return d?(i["--n-group-text-color"]=t.groupTextColorInverted,i["--n-color"]=t.colorInverted,i["--n-item-text-color"]=t.itemTextColorInverted,i["--n-item-text-color-hover"]=t.itemTextColorHoverInverted,i["--n-item-text-color-active"]=t.itemTextColorActiveInverted,i["--n-item-text-color-child-active"]=t.itemTextColorChildActiveInverted,i["--n-item-text-color-child-active-hover"]=t.itemTextColorChildActiveInverted,i["--n-item-text-color-active-hover"]=t.itemTextColorActiveHoverInverted,i["--n-item-icon-color"]=t.itemIconColorInverted,i["--n-item-icon-color-hover"]=t.itemIconColorHoverInverted,i["--n-item-icon-color-active"]=t.itemIconColorActiveInverted,i["--n-item-icon-color-active-hover"]=t.itemIconColorActiveHoverInverted,i["--n-item-icon-color-child-active"]=t.itemIconColorChildActiveInverted,i["--n-item-icon-color-child-active-hover"]=t.itemIconColorChildActiveHoverInverted,i["--n-item-icon-color-collapsed"]=t.itemIconColorCollapsedInverted,i["--n-item-text-color-horizontal"]=t.itemTextColorHorizontalInverted,i["--n-item-text-color-hover-horizontal"]=t.itemTextColorHoverHorizontalInverted,i["--n-item-text-color-active-horizontal"]=t.itemTextColorActiveHorizontalInverted,i["--n-item-text-color-child-active-horizontal"]=t.itemTextColorChildActiveHorizontalInverted,i["--n-item-text-color-child-active-hover-horizontal"]=t.itemTextColorChildActiveHoverHorizontalInverted,i["--n-item-text-color-active-hover-horizontal"]=t.itemTextColorActiveHoverHorizontalInverted,i["--n-item-icon-color-horizontal"]=t.itemIconColorHorizontalInverted,i["--n-item-icon-color-hover-horizontal"]=t.itemIconColorHoverHorizontalInverted,i["--n-item-icon-color-active-horizontal"]=t.itemIconColorActiveHorizontalInverted,i["--n-item-icon-color-active-hover-horizontal"]=t.itemIconColorActiveHoverHorizontalInverted,i["--n-item-icon-color-child-active-horizontal"]=t.itemIconColorChildActiveHorizontalInverted,i["--n-item-icon-color-child-active-hover-horizontal"]=t.itemIconColorChildActiveHoverHorizontalInverted,i["--n-arrow-color"]=t.arrowColorInverted,i["--n-arrow-color-hover"]=t.arrowColorHoverInverted,i["--n-arrow-color-active"]=t.arrowColorActiveInverted,i["--n-arrow-color-active-hover"]=t.arrowColorActiveHoverInverted,i["--n-arrow-color-child-active"]=t.arrowColorChildActiveInverted,i["--n-arrow-color-child-active-hover"]=t.arrowColorChildActiveHoverInverted,i["--n-item-color-hover"]=t.itemColorHoverInverted,i["--n-item-color-active"]=t.itemColorActiveInverted,i["--n-item-color-active-hover"]=t.itemColorActiveHoverInverted,i["--n-item-color-active-collapsed"]=t.itemColorActiveCollapsedInverted):(i["--n-group-text-color"]=t.groupTextColor,i["--n-color"]=t.color,i["--n-item-text-color"]=t.itemTextColor,i["--n-item-text-color-hover"]=t.itemTextColorHover,i["--n-item-text-color-active"]=t.itemTextColorActive,i["--n-item-text-color-child-active"]=t.itemTextColorChildActive,i["--n-item-text-color-child-active-hover"]=t.itemTextColorChildActiveHover,i["--n-item-text-color-active-hover"]=t.itemTextColorActiveHover,i["--n-item-icon-color"]=t.itemIconColor,i["--n-item-icon-color-hover"]=t.itemIconColorHover,i["--n-item-icon-color-active"]=t.itemIconColorActive,i["--n-item-icon-color-active-hover"]=t.itemIconColorActiveHover,i["--n-item-icon-color-child-active"]=t.itemIconColorChildActive,i["--n-item-icon-color-child-active-hover"]=t.itemIconColorChildActiveHover,i["--n-item-icon-color-collapsed"]=t.itemIconColorCollapsed,i["--n-item-text-color-horizontal"]=t.itemTextColorHorizontal,i["--n-item-text-color-hover-horizontal"]=t.itemTextColorHoverHorizontal,i["--n-item-text-color-active-horizontal"]=t.itemTextColorActiveHorizontal,i["--n-item-text-color-child-active-horizontal"]=t.itemTextColorChildActiveHorizontal,i["--n-item-text-color-child-active-hover-horizontal"]=t.itemTextColorChildActiveHoverHorizontal,i["--n-item-text-color-active-hover-horizontal"]=t.itemTextColorActiveHoverHorizontal,i["--n-item-icon-color-horizontal"]=t.itemIconColorHorizontal,i["--n-item-icon-color-hover-horizontal"]=t.itemIconColorHoverHorizontal,i["--n-item-icon-color-active-horizontal"]=t.itemIconColorActiveHorizontal,i["--n-item-icon-color-active-hover-horizontal"]=t.itemIconColorActiveHoverHorizontal,i["--n-item-icon-color-child-active-horizontal"]=t.itemIconColorChildActiveHorizontal,i["--n-item-icon-color-child-active-hover-horizontal"]=t.itemIconColorChildActiveHoverHorizontal,i["--n-arrow-color"]=t.arrowColor,i["--n-arrow-color-hover"]=t.arrowColorHover,i["--n-arrow-color-active"]=t.arrowColorActive,i["--n-arrow-color-active-hover"]=t.arrowColorActiveHover,i["--n-arrow-color-child-active"]=t.arrowColorChildActive,i["--n-arrow-color-child-active-hover"]=t.arrowColorChildActiveHover,i["--n-item-color-hover"]=t.itemColorHover,i["--n-item-color-active"]=t.itemColorActive,i["--n-item-color-active-hover"]=t.itemColorActiveHover,i["--n-item-color-active-collapsed"]=t.itemColorActiveCollapsed),i}),z=o?He("menu",y(()=>e.inverted?"a":"b"),h,e):void 0,E=io(),F=M(null),D=M(null);let Y=!0;const W=()=>{var d;Y?Y=!1:(d=F.value)===null||d===void 0||d.sync({showAllItemsBeforeCalculate:!0})};function ne(){return document.getElementById(E)}const U=M(-1);function se(d){U.value=e.options.length-d}function de(d){d||(U.value=-1)}const ue=y(()=>{const d=U.value;return{children:d===-1?[]:e.options.slice(d)}}),ve=y(()=>{const{childrenField:d,disabledField:m,keyField:t}=e;return be([ue.value],{getIgnored(g){return Ie(g)},getChildren(g){return g[d]},getDisabled(g){return g[m]},getKey(g){var H;return(H=g[t])!==null&&H!==void 0?H:g.name}})}),me=y(()=>be([{}]).treeNodes[0]);function he(){var d;if(U.value===-1)return p(we,{root:!0,level:0,key:"__ellpisisGroupPlaceholder__",internalKey:"__ellpisisGroupPlaceholder__",title:"···",tmNode:me.value,domId:E,isEllipsisPlaceholder:!0});const m=ve.value.treeNodes[0],t=$.value,g=!!(!((d=m.children)===null||d===void 0)&&d.some(H=>t.includes(H.key)));return p(we,{level:0,root:!0,key:"__ellpisisGroup__",internalKey:"__ellpisisGroup__",title:"···",virtualChildActive:g,tmNode:m,domId:E,rawNodes:m.rawNode.children||[],tmNodes:m.children||[],isEllipsisPlaceholder:!0})}return{mergedClsPrefix:r,controlledExpandedKeys:N,uncontrolledExpanededKeys:v,mergedExpandedKeys:P,uncontrolledValue:f,mergedValue:w,activePath:$,tmNodes:T,mergedTheme:n,mergedCollapsed:l,cssVars:o?void 0:h,themeClass:z==null?void 0:z.themeClass,overflowRef:F,counterRef:D,updateCounter:()=>{},onResize:W,onUpdateOverflow:de,onUpdateCount:se,renderCounter:he,getCounter:ne,onRender:z==null?void 0:z.onRender,showOption:V,deriveResponsiveState:W}},render(){const{mergedClsPrefix:e,mode:r,themeClass:o,onRender:n}=this;n==null||n();const a=()=>this.tmNodes.map(c=>Pe(c,this.$props)),s=r==="horizontal"&&this.responsive,u=()=>p("div",lo(this.$attrs,{role:r==="horizontal"?"menubar":"menu",class:[`${e}-menu`,o,`${e}-menu--${r}`,s&&`${e}-menu--responsive`,this.mergedCollapsed&&`${e}-menu--collapsed`],style:this.cssVars}),s?p(Oo,{ref:"overflowRef",onUpdateOverflow:this.onUpdateOverflow,getCounter:this.getCounter,onUpdateCount:this.onUpdateCount,updateCounter:this.updateCounter,style:{width:"100%",display:"flex",overflow:"hidden"}},{default:a,counter:this.renderCounter}):a());return s?p(no,{onResize:this.onResize},{default:u}):u()}}),ft={xmlns:"http://www.w3.org/2000/svg","xmlns:xlink":"http://www.w3.org/1999/xlink",viewBox:"0 0 512 512"},gt=B("path",{d:"M428 224H288a48 48 0 0 1-48-48V36a4 4 0 0 0-4-4h-92a64 64 0 0 0-64 64v320a64 64 0 0 0 64 64h224a64 64 0 0 0 64-64V228a4 4 0 0 0-4-4zm-92 160H176a16 16 0 0 1 0-32h160a16 16 0 0 1 0 32zm0-80H176a16 16 0 0 1 0-32h160a16 16 0 0 1 0 32z",fill:"currentColor"},null,-1),bt=B("path",{d:"M419.22 188.59L275.41 44.78a2 2 0 0 0-3.41 1.41V176a16 16 0 0 0 16 16h129.81a2 2 0 0 0 1.41-3.41z",fill:"currentColor"},null,-1),Ct=[gt,bt],Be=O({name:"DocumentText",render:function(r,o){return X(),ae("svg",ft,Ct)}}),xt={xmlns:"http://www.w3.org/2000/svg","xmlns:xlink":"http://www.w3.org/1999/xlink",viewBox:"0 0 512 512"},yt=B("path",{d:"M427.68 351.43C402 320 383.87 304 383.87 217.35C383.87 138 343.35 109.73 310 96c-4.43-1.82-8.6-6-9.95-10.55C294.2 65.54 277.8 48 256 48s-38.21 17.55-44 37.47c-1.35 4.6-5.52 8.71-9.95 10.53c-33.39 13.75-73.87 41.92-73.87 121.35C128.13 304 110 320 84.32 351.43C73.68 364.45 83 384 101.61 384h308.88c18.51 0 27.77-19.61 17.19-32.57z",fill:"none",stroke:"currentColor","stroke-linecap":"round","stroke-linejoin":"round","stroke-width":"32"},null,-1),zt=B("path",{d:"M320 384v16a64 64 0 0 1-128 0v-16",fill:"none",stroke:"currentColor","stroke-linecap":"round","stroke-linejoin":"round","stroke-width":"32"},null,-1),It=[yt,zt],Ce=O({name:"NotificationsOutline",render:function(r,o){return X(),ae("svg",xt,It)}}),wt={getChannels:()=>k.get("/notifications/channels"),getChannel:e=>k.get(`/notifications/channels/${e}`),createChannel:e=>k.post("/notifications/channels",e),updateChannel:(e,r)=>k.put(`/notifications/channels/${e}`,r),deleteChannel:e=>k.delete(`/notifications/channels/${e}`),testChannel:e=>k.post(`/notifications/test/${e}`),getHistory:e=>k.get("/notifications/history",{params:e}),deleteHistory:e=>k.delete(`/notifications/history/${e}`),getTypes:()=>k.get("/notifications/types"),getTargetRules:e=>k.get("/notifications/target-rules",{params:e}),createTargetRule:e=>k.post("/notifications/target-rules",e),getTargetRule:e=>k.get(`/notifications/target-rules/${e}`),updateTargetRule:(e,r)=>k.put(`/notifications/target-rules/${e}`,r),deleteTargetRule:e=>k.delete(`/notifications/target-rules/${e}`),toggleTargetRule:e=>k.post(`/notifications/target-rules/${e}/toggle`),getTargets:e=>k.get("/notifications/targets",{params:e}),createTarget:e=>k.post("/notifications/targets",e),getTarget:e=>k.get(`/notifications/targets/${e}`),deleteTarget:e=>k.delete(`/notifications/targets/${e}`),send:e=>k.post("/notifications/send",e),sendAlert:e=>k.post("/notifications/alert",e)},_t={style:{"font-size":"13px"},class:"mobile-username"},Ht={class:"logo-text"},kt={style:{"font-size":"13px"}},At={class:"page"},Rt={__name:"index",setup(e){const r=so(),o=uo(),n=ao(),a=yo(),l=M(!1),s=M(!1),u=M(0),c=y(()=>o.path),f=M([]),A=y(()=>{try{const h=localStorage.getItem("user");if(h)return JSON.parse(h).username||"admin"}catch{}return"admin"});function w(h){return()=>p(h)}const v=[{key:"/dashboard",label:"仪表盘",icon:w(Mo)},{key:"monitoring",label:"监控中心",icon:w($e),children:[{key:"/monitoring/devices",label:"设备监控"},{key:"/monitoring/alerts",label:"告警管理"},{key:"/monitoring/performance",label:"性能监控"}]},{key:"workorder",label:"工单管理",icon:w(Fo),children:[{key:"/workorder/list",label:"工单列表"},{key:"/workorder/create",label:"创建工单"},{key:"/workorder/my",label:"我的工单"}]},{key:"knowledge",label:"知识库",icon:w(Ko),children:[{key:"/knowledge/list",label:"知识文档"},{key:"/knowledge/category",label:"分类管理"},{key:"/knowledge/cases",label:"故障案例"}]},{key:"ai",label:"AI助手",icon:w(jo),children:[{key:"/ai/chat",label:"AI 聊天"},{key:"/ai/copilot",label:"知识库问答"},{key:"/ai/analyze",label:"智能分析"}]},{key:"automation",label:"自动化",icon:w(Bo),children:[{key:"/automation/script",label:"脚本管理"},{key:"/automation/task",label:"任务调度"},{key:"/automation/evaluate",label:"指标评估"},{key:"/automation/execute",label:"执行记录"}]},{key:"backup",label:"备份管理",icon:w(Be),children:[{key:"/backup/list",label:"备份记录"},{key:"/backup/restore",label:"恢复管理"}]},{key:"report",label:"报表管理",icon:w(Be),children:[{key:"/report/list",label:"报表管理"},{key:"/report/create",label:"生成报表"},{key:"/report/template",label:"模板管理"}]},{key:"notification",label:"消息中心",icon:w(Ce),children:[{key:"/notification/message",label:"我的消息"},{key:"/notification/history",label:"消息历史"},{key:"/notification/config",label:"通知配置"}]},{key:"system",label:"系统管理",icon:w(Lo),children:[{key:"/system/user",label:"用户管理"},{key:"/system/role",label:"角色管理"},{key:"/system/menu",label:"菜单管理"},{key:"/system/dict",label:"字典管理"},{key:"/system/config",label:"参数配置"},{key:"/system/logs",label:"日志查看"},{key:"/system/adapters",label:"适配器管理"}]}],S=y(()=>{const h=[];return o.matched.forEach(z=>{z.meta.title&&h.push(z.meta.title)}),h.length?h:["仪表盘"]});function N(){r.push("/dashboard")}function P(){l.value=!l.value}function T(h,z){z.children===void 0&&r.push(h)}function $(h){f.value=h.length>0?[h[h.length-1]]:[]}const J=[{label:"个人中心",key:"profile"},{label:"修改密码",key:"password"},{type:"divider",key:"d1"},{label:"退出登录",key:"logout"}];function L(h){h==="logout"?a.warning({title:"退出确认",content:"确定要退出登录吗？",positiveText:"确定",negativeText:"取消",onPositiveClick:async()=>{try{await fetch("/api/v1/auth/logout",{method:"POST",headers:{Authorization:`Bearer ${localStorage.getItem("token")||""}`}})}catch{}localStorage.removeItem("token"),localStorage.removeItem("user"),n.success("已退出登录"),window.location.href="/login"}}):h==="password"?n.info("修改密码功能开发中"):h==="profile"&&n.info("个人中心功能开发中")}const j=async()=>{try{const h=await wt.getHistory({page:1,page_size:1});u.value=(h==null?void 0:h.total)||(Array.isArray(h)?h.length:0)}catch(h){console.warn("Failed to fetch notification count:",h)}},V=()=>{s.value=window.innerWidth<768,s.value&&(l.value=!0)};return Fe(()=>{V(),window.addEventListener("resize",V),j();const h=setInterval(j,6e4);ye(()=>clearInterval(h))}),co(()=>o.path,()=>{const h=v.find(z=>{var E;return(E=z.children)==null?void 0:E.some(F=>F.key===o.path)});h&&(f.value=[h.key])},{immediate:!0}),ye(()=>{window.removeEventListener("resize",V)}),(h,z)=>{const E=Vo,F=mo,D=Ro,Y=So,W=No,ne=je,U=it,se=pt,de=ko,ue=Wo,ve=Zo,me=vo("router-view"),he=Ao,d=_o;return X(),Te(d,{"has-sider":"",class:"layout","native-scrollbar":!1},{default:_(()=>[I(U,{class:"mobile-header"},{default:_(()=>[I(D,{align:"center"},{default:_(()=>[I(F,{quaternary:"",circle:"",size:"small",onClick:P},{icon:_(()=>[I(E,null,{default:_(()=>[I(ie(Ho))]),_:1})]),_:1}),z[4]||(z[4]=B("span",{class:"mobile-title"},"ITOps",-1))]),_:1}),I(D,{align:"center"},{default:_(()=>[I(Y,{value:u.value,max:99,show:u.value>0},{default:_(()=>[I(F,{quaternary:"",circle:"",size:"small",onClick:z[0]||(z[0]=m=>h.$router.push("/notification/message"))},{icon:_(()=>[I(E,null,{default:_(()=>[I(ie(Ce))]),_:1})]),_:1})]),_:1},8,["value","show"]),I(ne,{options:J,onSelect:L},{default:_(()=>[I(D,{align:"center",style:{cursor:"pointer",padding:"0 8px"}},{default:_(()=>[I(W,{round:"",size:"small",style:{background:"#18a058"}},{default:_(()=>[ge(oe(A.value.charAt(0).toUpperCase()),1)]),_:1}),B("span",_t,oe(A.value),1)]),_:1})]),_:1})]),_:1})]),_:1}),I(de,{bordered:"",collapsed:l.value,"collapsed-width":64,width:220,"show-trigger":"bar","collapse-mode":"width","native-scrollbar":!1,class:po(["sider",{"mobile-sider":s.value}]),style:ho(s.value&&!l.value?{position:"fixed",left:0,top:0,bottom:0,zIndex:1e3,transform:"translateX(-100%)",transition:"transform 0.3s"}:{})},{default:_(()=>[s.value&&!l.value?(X(),ae("div",{key:0,class:"sidebar-overlay",onClick:z[1]||(z[1]=m=>l.value=!0)})):fo("",!0),B("div",{class:"logo",onClick:N},[I(E,{size:"26",color:"#18a058"},{default:_(()=>[I(ie($e))]),_:1}),go(B("span",Ht,"ITOps",512),[[bo,!l.value]])]),I(se,{collapsed:l.value,"collapsed-width":64,"collapsed-icon-size":22,options:v,value:c.value,"expanded-keys":f.value,indent:16,"onUpdate:value":z[2]||(z[2]=(m,t)=>T(m,t)),"onUpdate:expandedKeys":$},null,8,["collapsed","value","expanded-keys"])]),_:1},8,["collapsed","class","style"]),I(d,{class:"main"},{default:_(()=>[I(U,{class:"header"},{default:_(()=>[I(ve,null,{default:_(()=>[(X(!0),ae(Ke,null,Co(S.value,m=>(X(),Te(ue,{key:m},{default:_(()=>[ge(oe(m),1)]),_:2},1024))),128))]),_:1}),I(D,{align:"center",class:"desktop-only"},{default:_(()=>[I(Y,{value:u.value,max:99,show:u.value>0},{default:_(()=>[I(F,{quaternary:"",circle:"",size:"small",onClick:z[3]||(z[3]=m=>h.$router.push("/notification/message"))},{icon:_(()=>[I(E,null,{default:_(()=>[I(ie(Ce))]),_:1})]),_:1})]),_:1},8,["value","show"]),I(ne,{options:J,onSelect:L},{default:_(()=>[I(D,{align:"center",style:{cursor:"pointer",padding:"0 8px"}},{default:_(()=>[I(W,{round:"",size:"small",style:{background:"#18a058"}},{default:_(()=>[ge(oe(A.value.charAt(0).toUpperCase()),1)]),_:1}),B("span",kt,oe(A.value),1)]),_:1})]),_:1})]),_:1})]),_:1}),I(he,{class:"content","native-scrollbar":!1},{default:_(()=>[B("div",At,[I(me)])]),_:1})]),_:1})]),_:1})}}},Yt=xo(Rt,[["__scopeId","data-v-cda8a708"]]);export{Yt as default};
