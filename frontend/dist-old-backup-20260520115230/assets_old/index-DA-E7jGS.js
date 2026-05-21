import{i as $,j as h,k as Ee,l as C,m as b,n as R,p as x,q as Ie,s as Y,v as ke,x as y,y as ce,z as re,A as be,h as E,o as Be,C as ye,D as Qe,E as j,F as Ye,G as We,H as pe,I as oe,J as eo,K as Q,N as oo,L as He,M as ze,O as Fe,P as fe,Q as to,V as ro,R as Ne,S as no,T as io,U as q,d as B,c as X,a as P,W as lo,X as $e,w as I,u as ao,Y as co,Z as so,b as z,B as uo,e as le,g as ge,t as te,_ as vo,$ as mo,a0 as ho,a1 as po,a2 as fo,a3 as go}from"./index-DeEsbs8n.js";import{r as H}from"./request-BNeF-5TW.js";import{_ as Co}from"./_plugin-vue_export-helper-DlAUqK2U.js";import{u as xo}from"./composables-ctiFUjii.js";import{l as bo,p as yo,a as zo,_ as wo,b as _o,c as Io,d as ko}from"./LayoutSider-DR9v8mG7.js";import{u as Ho,_ as Ao}from"./Space-CucXZsRf.js";import{N as Ro}from"./Badge-CQ0_3ngV.js";import{d as So,_ as Ke}from"./Dropdown-BXjbnM7I.js";import{S as Te}from"./ServerOutline-CxMdOyZM.js";import{t as Po,_ as No}from"./Tooltip-D0_L80OS.js";import{a as Oe,u as $o}from"./use-message-CzWsbTRb.js";import{V as To,c as Ce}from"./create-CaAIucQk.js";import{G as Oo,F as Mo,S as Lo}from"./SettingsOutline-BvTemps6.js";import{T as Eo}from"./TicketOutline-sUdQ4UdF.js";import{N as Bo}from"./Icon-CAHWSlye.js";import"./use-keyboard-C3jg1LL-.js";import"./create-ref-setter-C4J8sofl.js";const Fo=$({name:"ChevronDownFilled",render(){return h("svg",{viewBox:"0 0 16 16",fill:"none",xmlns:"http://www.w3.org/2000/svg"},h("path",{d:"M3.20041 5.73966C3.48226 5.43613 3.95681 5.41856 4.26034 5.70041L8 9.22652L11.7397 5.70041C12.0432 5.41856 12.5177 5.43613 12.7996 5.73966C13.0815 6.0432 13.0639 6.51775 12.7603 6.7996L8.51034 10.7996C8.22258 11.0668 7.77743 11.0668 7.48967 10.7996L3.23966 6.7996C2.93613 6.51775 2.91856 6.0432 3.20041 5.73966Z",fill:"currentColor"}))}}),Ko={fontWeightActive:"400"};function jo(e){const{fontSize:r,textColor3:o,textColor2:n,borderRadius:a,buttonColor2Hover:l,buttonColor2Pressed:s}=e;return Object.assign(Object.assign({},Ko),{fontSize:r,itemLineHeight:"1.25",itemTextColor:o,itemTextColorHover:n,itemTextColorPressed:n,itemTextColorActive:n,itemBorderRadius:a,itemColorHover:l,itemColorPressed:s,separatorColor:o})}const Vo={common:Ee,self:jo},Do=C("breadcrumb",`
 white-space: nowrap;
 cursor: default;
 line-height: var(--n-item-line-height);
`,[b("ul",`
 list-style: none;
 padding: 0;
 margin: 0;
 `),b("a",`
 color: inherit;
 text-decoration: inherit;
 `),C("breadcrumb-item",`
 font-size: var(--n-font-size);
 transition: color .3s var(--n-bezier);
 display: inline-flex;
 align-items: center;
 `,[C("icon",`
 font-size: 18px;
 vertical-align: -.2em;
 transition: color .3s var(--n-bezier);
 color: var(--n-item-text-color);
 `),b("&:not(:last-child)",[R("clickable",[x("link",`
 cursor: pointer;
 `,[b("&:hover",`
 background-color: var(--n-item-color-hover);
 `),b("&:active",`
 background-color: var(--n-item-color-pressed); 
 `)])])]),x("link",`
 padding: 4px;
 border-radius: var(--n-item-border-radius);
 transition:
 background-color .3s var(--n-bezier),
 color .3s var(--n-bezier);
 color: var(--n-item-text-color);
 position: relative;
 `,[b("&:hover",`
 color: var(--n-item-text-color-hover);
 `,[C("icon",`
 color: var(--n-item-text-color-hover);
 `)]),b("&:active",`
 color: var(--n-item-text-color-pressed);
 `,[C("icon",`
 color: var(--n-item-text-color-pressed);
 `)])]),x("separator",`
 margin: 0 8px;
 color: var(--n-separator-color);
 transition: color .3s var(--n-bezier);
 user-select: none;
 -webkit-user-select: none;
 `),b("&:last-child",[x("link",`
 font-weight: var(--n-font-weight-active);
 cursor: unset;
 color: var(--n-item-text-color-active);
 `,[C("icon",`
 color: var(--n-item-text-color-active);
 `)]),x("separator",`
 display: none;
 `)])])]),je=ce("n-breadcrumb"),Uo=Object.assign(Object.assign({},Y.props),{separator:{type:String,default:"/"}}),Go=$({name:"Breadcrumb",props:Uo,setup(e){const{mergedClsPrefixRef:r,inlineThemeDisabled:o}=Ie(e),n=Y("Breadcrumb","-breadcrumb",Do,Vo,e,r);re(je,{separatorRef:be(e,"separator"),mergedClsPrefixRef:r});const a=y(()=>{const{common:{cubicBezierEaseInOut:s},self:{separatorColor:u,itemTextColor:c,itemTextColorHover:p,itemTextColorPressed:A,itemTextColorActive:w,fontSize:v,fontWeightActive:S,itemBorderRadius:T,itemColorHover:N,itemColorPressed:O,itemLineHeight:M}}=n.value;return{"--n-font-size":v,"--n-bezier":s,"--n-item-text-color":c,"--n-item-text-color-hover":p,"--n-item-text-color-pressed":A,"--n-item-text-color-active":w,"--n-separator-color":u,"--n-item-color-hover":N,"--n-item-color-pressed":O,"--n-item-border-radius":T,"--n-font-weight-active":S,"--n-item-line-height":M}}),l=o?ke("breadcrumb",void 0,a,e):void 0;return{mergedClsPrefix:r,cssVars:o?void 0:a,themeClass:l==null?void 0:l.themeClass,onRender:l==null?void 0:l.onRender}},render(){var e;return(e=this.onRender)===null||e===void 0||e.call(this),h("nav",{class:[`${this.mergedClsPrefix}-breadcrumb`,this.themeClass],style:this.cssVars,"aria-label":"Breadcrumb"},h("ul",null,this.$slots))}});function qo(e=Qe?window:null){const r=()=>{const{hash:a,host:l,hostname:s,href:u,origin:c,pathname:p,port:A,protocol:w,search:v}=(e==null?void 0:e.location)||{};return{hash:a,host:l,hostname:s,href:u,origin:c,pathname:p,port:A,protocol:w,search:v}},o=E(r()),n=()=>{o.value=r()};return Be(()=>{e&&(e.addEventListener("popstate",n),e.addEventListener("hashchange",n))}),ye(()=>{e&&(e.removeEventListener("popstate",n),e.removeEventListener("hashchange",n))}),o}const Jo={separator:String,href:String,clickable:{type:Boolean,default:!0},onClick:Function},Xo=$({name:"BreadcrumbItem",props:Jo,slots:Object,setup(e,{slots:r}){const o=j(je,null);if(!o)return()=>null;const{separatorRef:n,mergedClsPrefixRef:a}=o,l=qo(),s=y(()=>e.href?"a":"span"),u=y(()=>l.value.href===e.href?"location":null);return()=>{const{value:c}=a;return h("li",{class:[`${c}-breadcrumb-item`,e.clickable&&`${c}-breadcrumb-item--clickable`]},h(s.value,{class:`${c}-breadcrumb-item__link`,"aria-current":u.value,href:e.href,onClick:e.onClick},r),h("span",{class:`${c}-breadcrumb-item__separator`,"aria-hidden":"true"},Ye(r.separator,()=>{var p;return[(p=e.separator)!==null&&p!==void 0?p:n.value]})))}}});function Zo(e,r,o,n){return{itemColorHoverInverted:"#0000",itemColorActiveInverted:r,itemColorActiveHoverInverted:r,itemColorActiveCollapsedInverted:r,itemTextColorInverted:e,itemTextColorHoverInverted:o,itemTextColorChildActiveInverted:o,itemTextColorChildActiveHoverInverted:o,itemTextColorActiveInverted:o,itemTextColorActiveHoverInverted:o,itemTextColorHorizontalInverted:e,itemTextColorHoverHorizontalInverted:o,itemTextColorChildActiveHorizontalInverted:o,itemTextColorChildActiveHoverHorizontalInverted:o,itemTextColorActiveHorizontalInverted:o,itemTextColorActiveHoverHorizontalInverted:o,itemIconColorInverted:e,itemIconColorHoverInverted:o,itemIconColorActiveInverted:o,itemIconColorActiveHoverInverted:o,itemIconColorChildActiveInverted:o,itemIconColorChildActiveHoverInverted:o,itemIconColorCollapsedInverted:e,itemIconColorHorizontalInverted:e,itemIconColorHoverHorizontalInverted:o,itemIconColorActiveHorizontalInverted:o,itemIconColorActiveHoverHorizontalInverted:o,itemIconColorChildActiveHorizontalInverted:o,itemIconColorChildActiveHoverHorizontalInverted:o,arrowColorInverted:e,arrowColorHoverInverted:o,arrowColorActiveInverted:o,arrowColorActiveHoverInverted:o,arrowColorChildActiveInverted:o,arrowColorChildActiveHoverInverted:o,groupTextColorInverted:n}}function Qo(e){const{borderRadius:r,textColor3:o,primaryColor:n,textColor2:a,textColor1:l,fontSize:s,dividerColor:u,hoverColor:c,primaryColorHover:p}=e;return Object.assign({borderRadius:r,color:"#0000",groupTextColor:o,itemColorHover:c,itemColorActive:pe(n,{alpha:.1}),itemColorActiveHover:pe(n,{alpha:.1}),itemColorActiveCollapsed:pe(n,{alpha:.1}),itemTextColor:a,itemTextColorHover:a,itemTextColorActive:n,itemTextColorActiveHover:n,itemTextColorChildActive:n,itemTextColorChildActiveHover:n,itemTextColorHorizontal:a,itemTextColorHoverHorizontal:p,itemTextColorActiveHorizontal:n,itemTextColorActiveHoverHorizontal:n,itemTextColorChildActiveHorizontal:n,itemTextColorChildActiveHoverHorizontal:n,itemIconColor:l,itemIconColorHover:l,itemIconColorActive:n,itemIconColorActiveHover:n,itemIconColorChildActive:n,itemIconColorChildActiveHover:n,itemIconColorCollapsed:l,itemIconColorHorizontal:l,itemIconColorHoverHorizontal:p,itemIconColorActiveHorizontal:n,itemIconColorActiveHoverHorizontal:n,itemIconColorChildActiveHorizontal:n,itemIconColorChildActiveHoverHorizontal:n,itemHeight:"42px",arrowColor:a,arrowColorHover:a,arrowColorActive:n,arrowColorActiveHover:n,arrowColorChildActive:n,arrowColorChildActiveHover:n,colorInverted:"#0000",borderColorHorizontal:"#0000",fontSize:s,dividerColor:u},Zo("#BBB",n,"#FFF","#AAA"))}const Yo=We({name:"Menu",common:Ee,peers:{Tooltip:Po,Dropdown:So},self:Qo}),Wo=C("layout-header",`
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
 `)]),et={position:yo,inverted:Boolean,bordered:{type:Boolean,default:!1}},ot=$({name:"LayoutHeader",props:Object.assign(Object.assign({},Y.props),et),setup(e){const{mergedClsPrefixRef:r,inlineThemeDisabled:o}=Ie(e),n=Y("Layout","-layout-header",Wo,bo,e,r),a=y(()=>{const{common:{cubicBezierEaseInOut:s},self:u}=n.value,c={"--n-bezier":s};return e.inverted?(c["--n-color"]=u.headerColorInverted,c["--n-text-color"]=u.textColorInverted,c["--n-border-color"]=u.headerBorderColorInverted):(c["--n-color"]=u.headerColor,c["--n-text-color"]=u.textColor,c["--n-border-color"]=u.headerBorderColor),c}),l=o?ke("layout-header",y(()=>e.inverted?"a":"b"),a,e):void 0;return{mergedClsPrefix:r,cssVars:o?void 0:a,themeClass:l==null?void 0:l.themeClass,onRender:l==null?void 0:l.onRender}},render(){var e;const{mergedClsPrefix:r}=this;return(e=this.onRender)===null||e===void 0||e.call(this),h("div",{class:[`${r}-layout-header`,this.themeClass,this.position&&`${r}-layout-header--${this.position}-positioned`,this.bordered&&`${r}-layout-header--bordered`],style:this.cssVars},this.$slots)}}),ne=ce("n-menu"),Ve=ce("n-submenu"),Ae=ce("n-menu-item-group"),Me=[b("&::before","background-color: var(--n-item-color-hover);"),x("arrow",`
 color: var(--n-arrow-color-hover);
 `),x("icon",`
 color: var(--n-item-icon-color-hover);
 `),C("menu-item-content-header",`
 color: var(--n-item-text-color-hover);
 `,[b("a",`
 color: var(--n-item-text-color-hover);
 `),x("extra",`
 color: var(--n-item-text-color-hover);
 `)])],Le=[x("icon",`
 color: var(--n-item-icon-color-hover-horizontal);
 `),C("menu-item-content-header",`
 color: var(--n-item-text-color-hover-horizontal);
 `,[b("a",`
 color: var(--n-item-text-color-hover-horizontal);
 `),x("extra",`
 color: var(--n-item-text-color-hover-horizontal);
 `)])],tt=b([C("menu",`
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
 `,[C("submenu","margin: 0;"),C("menu-item","margin: 0;"),C("menu-item-content",`
 padding: 0 20px;
 border-bottom: 2px solid #0000;
 `,[b("&::before","display: none;"),R("selected","border-bottom: 2px solid var(--n-border-color-horizontal)")]),C("menu-item-content",[R("selected",[x("icon","color: var(--n-item-icon-color-active-horizontal);"),C("menu-item-content-header",`
 color: var(--n-item-text-color-active-horizontal);
 `,[b("a","color: var(--n-item-text-color-active-horizontal);"),x("extra","color: var(--n-item-text-color-active-horizontal);")])]),R("child-active",`
 border-bottom: 2px solid var(--n-border-color-horizontal);
 `,[C("menu-item-content-header",`
 color: var(--n-item-text-color-child-active-horizontal);
 `,[b("a",`
 color: var(--n-item-text-color-child-active-horizontal);
 `),x("extra",`
 color: var(--n-item-text-color-child-active-horizontal);
 `)]),x("icon",`
 color: var(--n-item-icon-color-child-active-horizontal);
 `)]),oe("disabled",[oe("selected, child-active",[b("&:focus-within",Le)]),R("selected",[J(null,[x("icon","color: var(--n-item-icon-color-active-hover-horizontal);"),C("menu-item-content-header",`
 color: var(--n-item-text-color-active-hover-horizontal);
 `,[b("a","color: var(--n-item-text-color-active-hover-horizontal);"),x("extra","color: var(--n-item-text-color-active-hover-horizontal);")])])]),R("child-active",[J(null,[x("icon","color: var(--n-item-icon-color-child-active-hover-horizontal);"),C("menu-item-content-header",`
 color: var(--n-item-text-color-child-active-hover-horizontal);
 `,[b("a","color: var(--n-item-text-color-child-active-hover-horizontal);"),x("extra","color: var(--n-item-text-color-child-active-hover-horizontal);")])])]),J("border-bottom: 2px solid var(--n-border-color-horizontal);",Le)]),C("menu-item-content-header",[b("a","color: var(--n-item-text-color-horizontal);")])])]),oe("responsive",[C("menu-item-content-header",`
 overflow: hidden;
 text-overflow: ellipsis;
 `)]),R("collapsed",[C("menu-item-content",[R("selected",[b("&::before",`
 background-color: var(--n-item-color-active-collapsed) !important;
 `)]),C("menu-item-content-header","opacity: 0;"),x("arrow","opacity: 0;"),x("icon","color: var(--n-item-icon-color-collapsed);")])]),C("menu-item",`
 height: var(--n-item-height);
 margin-top: 6px;
 position: relative;
 `),C("menu-item-content",`
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
 `,[b("> *","z-index: 1;"),b("&::before",`
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
 `),R("collapsed",[x("arrow","transform: rotate(0);")]),R("selected",[b("&::before","background-color: var(--n-item-color-active);"),x("arrow","color: var(--n-arrow-color-active);"),x("icon","color: var(--n-item-icon-color-active);"),C("menu-item-content-header",`
 color: var(--n-item-text-color-active);
 `,[b("a","color: var(--n-item-text-color-active);"),x("extra","color: var(--n-item-text-color-active);")])]),R("child-active",[C("menu-item-content-header",`
 color: var(--n-item-text-color-child-active);
 `,[b("a",`
 color: var(--n-item-text-color-child-active);
 `),x("extra",`
 color: var(--n-item-text-color-child-active);
 `)]),x("arrow",`
 color: var(--n-arrow-color-child-active);
 `),x("icon",`
 color: var(--n-item-icon-color-child-active);
 `)]),oe("disabled",[oe("selected, child-active",[b("&:focus-within",Me)]),R("selected",[J(null,[x("arrow","color: var(--n-arrow-color-active-hover);"),x("icon","color: var(--n-item-icon-color-active-hover);"),C("menu-item-content-header",`
 color: var(--n-item-text-color-active-hover);
 `,[b("a","color: var(--n-item-text-color-active-hover);"),x("extra","color: var(--n-item-text-color-active-hover);")])])]),R("child-active",[J(null,[x("arrow","color: var(--n-arrow-color-child-active-hover);"),x("icon","color: var(--n-item-icon-color-child-active-hover);"),C("menu-item-content-header",`
 color: var(--n-item-text-color-child-active-hover);
 `,[b("a","color: var(--n-item-text-color-child-active-hover);"),x("extra","color: var(--n-item-text-color-child-active-hover);")])])]),R("selected",[J(null,[b("&::before","background-color: var(--n-item-color-active-hover);")])]),J(null,Me)]),x("icon",`
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
 `),x("arrow",`
 grid-area: arrow;
 font-size: 16px;
 color: var(--n-arrow-color);
 transform: rotate(180deg);
 opacity: 1;
 transition:
 color .3s var(--n-bezier),
 transform 0.2s var(--n-bezier),
 opacity 0.2s var(--n-bezier);
 `),C("menu-item-content-header",`
 grid-area: content;
 transition:
 color .3s var(--n-bezier),
 opacity .3s var(--n-bezier);
 opacity: 1;
 white-space: nowrap;
 color: var(--n-item-text-color);
 `,[b("a",`
 outline: none;
 text-decoration: none;
 transition: color .3s var(--n-bezier);
 color: var(--n-item-text-color);
 `,[b("&::before",`
 content: "";
 position: absolute;
 left: 0;
 right: 0;
 top: 0;
 bottom: 0;
 `)]),x("extra",`
 font-size: .93em;
 color: var(--n-group-text-color);
 transition: color .3s var(--n-bezier);
 `)])]),C("submenu",`
 cursor: pointer;
 position: relative;
 margin-top: 6px;
 `,[C("menu-item-content",`
 height: var(--n-item-height);
 `),C("submenu-children",`
 overflow: hidden;
 padding: 0;
 `,[eo({duration:".2s"})])]),C("menu-item-group",[C("menu-item-group-title",`
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
 `)])]),C("menu-tooltip",[b("a",`
 color: inherit;
 text-decoration: none;
 `)]),C("menu-divider",`
 transition: background-color .3s var(--n-bezier);
 background-color: var(--n-divider-color);
 height: 1px;
 margin: 6px 18px;
 `)]);function J(e,r){return[R("hover",e,r),b("&:hover",e,r)]}const De=$({name:"MenuOptionContent",props:{collapsed:Boolean,disabled:Boolean,title:[String,Function],icon:Function,extra:[String,Function],showArrow:Boolean,childActive:Boolean,hover:Boolean,paddingLeft:Number,selected:Boolean,maxIconSize:{type:Number,required:!0},activeIconSize:{type:Number,required:!0},iconMarginRight:{type:Number,required:!0},clsPrefix:{type:String,required:!0},onClick:Function,tmNode:{type:Object,required:!0},isEllipsisPlaceholder:Boolean},setup(e){const{props:r}=j(ne);return{menuProps:r,style:y(()=>{const{paddingLeft:o}=e;return{paddingLeft:o&&`${o}px`}}),iconStyle:y(()=>{const{maxIconSize:o,activeIconSize:n,iconMarginRight:a}=e;return{width:`${o}px`,height:`${o}px`,fontSize:`${n}px`,marginRight:`${a}px`}})}},render(){const{clsPrefix:e,tmNode:r,menuProps:{renderIcon:o,renderLabel:n,renderExtra:a,expandIcon:l}}=this,s=o?o(r.rawNode):Q(this.icon);return h("div",{onClick:u=>{var c;(c=this.onClick)===null||c===void 0||c.call(this,u)},role:"none",class:[`${e}-menu-item-content`,{[`${e}-menu-item-content--selected`]:this.selected,[`${e}-menu-item-content--collapsed`]:this.collapsed,[`${e}-menu-item-content--child-active`]:this.childActive,[`${e}-menu-item-content--disabled`]:this.disabled,[`${e}-menu-item-content--hover`]:this.hover}],style:this.style},s&&h("div",{class:`${e}-menu-item-content__icon`,style:this.iconStyle,role:"none"},[s]),h("div",{class:`${e}-menu-item-content-header`,role:"none"},this.isEllipsisPlaceholder?this.title:n?n(r.rawNode):Q(this.title),this.extra||a?h("span",{class:`${e}-menu-item-content-header__extra`}," ",a?a(r.rawNode):Q(this.extra)):null),this.showArrow?h(oo,{ariaHidden:!0,class:`${e}-menu-item-content__arrow`,clsPrefix:e},{default:()=>l?l(r.rawNode):h(Fo,null)}):null)}}),ae=8;function Re(e){const r=j(ne),{props:o,mergedCollapsedRef:n}=r,a=j(Ve,null),l=j(Ae,null),s=y(()=>o.mode==="horizontal"),u=y(()=>s.value?o.dropdownPlacement:"tmNodes"in e?"right-start":"right"),c=y(()=>{var v;return Math.max((v=o.collapsedIconSize)!==null&&v!==void 0?v:o.iconSize,o.iconSize)}),p=y(()=>{var v;return!s.value&&e.root&&n.value&&(v=o.collapsedIconSize)!==null&&v!==void 0?v:o.iconSize}),A=y(()=>{if(s.value)return;const{collapsedWidth:v,indent:S,rootIndent:T}=o,{root:N,isGroup:O}=e,M=T===void 0?S:T;return N?n.value?v/2-c.value/2:M:l&&typeof l.paddingLeftRef.value=="number"?S/2+l.paddingLeftRef.value:a&&typeof a.paddingLeftRef.value=="number"?(O?S/2:S)+a.paddingLeftRef.value:0}),w=y(()=>{const{collapsedWidth:v,indent:S,rootIndent:T}=o,{value:N}=c,{root:O}=e;return s.value||!O||!n.value?ae:(T===void 0?S:T)+N+ae-(v+N)/2});return{dropdownPlacement:u,activeIconSize:p,maxIconSize:c,paddingLeft:A,iconMarginRight:w,NMenu:r,NSubmenu:a,NMenuOptionGroup:l}}const Se={internalKey:{type:[String,Number],required:!0},root:Boolean,isGroup:Boolean,level:{type:Number,required:!0},title:[String,Function],extra:[String,Function]},rt=$({name:"MenuDivider",setup(){const e=j(ne),{mergedClsPrefixRef:r,isHorizontalRef:o}=e;return()=>o.value?null:h("div",{class:`${r.value}-menu-divider`})}}),Ue=Object.assign(Object.assign({},Se),{tmNode:{type:Object,required:!0},disabled:Boolean,icon:Function,onClick:Function}),nt=He(Ue),it=$({name:"MenuOption",props:Ue,setup(e){const r=Re(e),{NSubmenu:o,NMenu:n,NMenuOptionGroup:a}=r,{props:l,mergedClsPrefixRef:s,mergedCollapsedRef:u}=n,c=o?o.mergedDisabledRef:a?a.mergedDisabledRef:{value:!1},p=y(()=>c.value||e.disabled);function A(v){const{onClick:S}=e;S&&S(v)}function w(v){p.value||(n.doSelect(e.internalKey,e.tmNode.rawNode),A(v))}return{mergedClsPrefix:s,dropdownPlacement:r.dropdownPlacement,paddingLeft:r.paddingLeft,iconMarginRight:r.iconMarginRight,maxIconSize:r.maxIconSize,activeIconSize:r.activeIconSize,mergedTheme:n.mergedThemeRef,menuProps:l,dropdownEnabled:ze(()=>e.root&&u.value&&l.mode!=="horizontal"&&!p.value),selected:ze(()=>n.mergedValueRef.value===e.internalKey),mergedDisabled:p,handleClick:w}},render(){const{mergedClsPrefix:e,mergedTheme:r,tmNode:o,menuProps:{renderLabel:n,nodeProps:a}}=this,l=a==null?void 0:a(o.rawNode);return h("div",Object.assign({},l,{role:"menuitem",class:[`${e}-menu-item`,l==null?void 0:l.class]}),h(No,{theme:r.peers.Tooltip,themeOverrides:r.peerOverrides.Tooltip,trigger:"hover",placement:this.dropdownPlacement,disabled:!this.dropdownEnabled||this.title===void 0,internalExtraClass:["menu-tooltip"]},{default:()=>n?n(o.rawNode):Q(this.title),trigger:()=>h(De,{tmNode:o,clsPrefix:e,paddingLeft:this.paddingLeft,iconMarginRight:this.iconMarginRight,maxIconSize:this.maxIconSize,activeIconSize:this.activeIconSize,selected:this.selected,title:this.title,extra:this.extra,disabled:this.mergedDisabled,icon:this.icon,onClick:this.handleClick})}))}}),Ge=Object.assign(Object.assign({},Se),{tmNode:{type:Object,required:!0},tmNodes:{type:Array,required:!0}}),lt=He(Ge),at=$({name:"MenuOptionGroup",props:Ge,setup(e){const r=Re(e),{NSubmenu:o}=r,n=y(()=>o!=null&&o.mergedDisabledRef.value?!0:e.tmNode.disabled);re(Ae,{paddingLeftRef:r.paddingLeft,mergedDisabledRef:n});const{mergedClsPrefixRef:a,props:l}=j(ne);return function(){const{value:s}=a,u=r.paddingLeft.value,{nodeProps:c}=l,p=c==null?void 0:c(e.tmNode.rawNode);return h("div",{class:`${s}-menu-item-group`,role:"group"},h("div",Object.assign({},p,{class:[`${s}-menu-item-group-title`,p==null?void 0:p.class],style:[(p==null?void 0:p.style)||"",u!==void 0?`padding-left: ${u}px;`:""]}),Q(e.title),e.extra?h(Fe,null," ",Q(e.extra)):null),h("div",null,e.tmNodes.map(A=>Pe(A,l))))}}});function we(e){return e.type==="divider"||e.type==="render"}function ct(e){return e.type==="divider"}function Pe(e,r){const{rawNode:o}=e,{show:n}=o;if(n===!1)return null;if(we(o))return ct(o)?h(rt,Object.assign({key:e.key},o.props)):null;const{labelField:a}=r,{key:l,level:s,isGroup:u}=e,c=Object.assign(Object.assign({},o),{title:o.title||o[a],extra:o.titleExtra||o.extra,key:l,internalKey:l,level:s,root:s===0,isGroup:u});return e.children?e.isGroup?h(at,fe(c,lt,{tmNode:e,tmNodes:e.children,key:l})):h(_e,fe(c,st,{key:l,rawNodes:o[r.childrenField],tmNodes:e.children,tmNode:e})):h(it,fe(c,nt,{key:l,tmNode:e}))}const qe=Object.assign(Object.assign({},Se),{rawNodes:{type:Array,default:()=>[]},tmNodes:{type:Array,default:()=>[]},tmNode:{type:Object,required:!0},disabled:Boolean,icon:Function,onClick:Function,domId:String,virtualChildActive:{type:Boolean,default:void 0},isEllipsisPlaceholder:Boolean}),st=He(qe),_e=$({name:"Submenu",props:qe,setup(e){const r=Re(e),{NMenu:o,NSubmenu:n}=r,{props:a,mergedCollapsedRef:l,mergedThemeRef:s}=o,u=y(()=>{const{disabled:v}=e;return n!=null&&n.mergedDisabledRef.value||a.disabled?!0:v}),c=E(!1);re(Ve,{paddingLeftRef:r.paddingLeft,mergedDisabledRef:u}),re(Ae,null);function p(){const{onClick:v}=e;v&&v()}function A(){u.value||(l.value||o.toggleExpand(e.internalKey),p())}function w(v){c.value=v}return{menuProps:a,mergedTheme:s,doSelect:o.doSelect,inverted:o.invertedRef,isHorizontal:o.isHorizontalRef,mergedClsPrefix:o.mergedClsPrefixRef,maxIconSize:r.maxIconSize,activeIconSize:r.activeIconSize,iconMarginRight:r.iconMarginRight,dropdownPlacement:r.dropdownPlacement,dropdownShow:c,paddingLeft:r.paddingLeft,mergedDisabled:u,mergedValue:o.mergedValueRef,childActive:ze(()=>{var v;return(v=e.virtualChildActive)!==null&&v!==void 0?v:o.activePathRef.value.includes(e.internalKey)}),collapsed:y(()=>a.mode==="horizontal"?!1:l.value?!0:!o.mergedExpandedKeysRef.value.includes(e.internalKey)),dropdownEnabled:y(()=>!u.value&&(a.mode==="horizontal"||l.value)),handlePopoverShowChange:w,handleClick:A}},render(){var e;const{mergedClsPrefix:r,menuProps:{renderIcon:o,renderLabel:n}}=this,a=()=>{const{isHorizontal:s,paddingLeft:u,collapsed:c,mergedDisabled:p,maxIconSize:A,activeIconSize:w,title:v,childActive:S,icon:T,handleClick:N,menuProps:{nodeProps:O},dropdownShow:M,iconMarginRight:Z,tmNode:F,mergedClsPrefix:V,isEllipsisPlaceholder:D,extra:m}=this,_=O==null?void 0:O(F.rawNode);return h("div",Object.assign({},_,{class:[`${V}-menu-item`,_==null?void 0:_.class],role:"menuitem"}),h(De,{tmNode:F,paddingLeft:u,collapsed:c,disabled:p,iconMarginRight:Z,maxIconSize:A,activeIconSize:w,title:v,extra:m,showArrow:!s,childActive:S,clsPrefix:V,icon:T,hover:M,onClick:N,isEllipsisPlaceholder:D}))},l=()=>h(to,null,{default:()=>{const{tmNodes:s,collapsed:u}=this;return u?null:h("div",{class:`${r}-submenu-children`,role:"menu"},s.map(c=>Pe(c,this.menuProps)))}});return this.root?h(Ke,Object.assign({size:"large",trigger:"hover"},(e=this.menuProps)===null||e===void 0?void 0:e.dropdownProps,{themeOverrides:this.mergedTheme.peerOverrides.Dropdown,theme:this.mergedTheme.peers.Dropdown,builtinThemeOverrides:{fontSizeLarge:"14px",optionIconSizeLarge:"18px"},value:this.mergedValue,disabled:!this.dropdownEnabled,placement:this.dropdownPlacement,keyField:this.menuProps.keyField,labelField:this.menuProps.labelField,childrenField:this.menuProps.childrenField,onUpdateShow:this.handlePopoverShowChange,options:this.rawNodes,onSelect:this.doSelect,inverted:this.inverted,renderIcon:o,renderLabel:n}),{default:()=>h("div",{class:`${r}-submenu`,role:"menu","aria-expanded":!this.collapsed,id:this.domId},a(),this.isHorizontal?null:l())}):h("div",{class:`${r}-submenu`,role:"menu","aria-expanded":!this.collapsed,id:this.domId},a(),l())}}),dt=Object.assign(Object.assign({},Y.props),{options:{type:Array,default:()=>[]},collapsed:{type:Boolean,default:void 0},collapsedWidth:{type:Number,default:48},iconSize:{type:Number,default:20},collapsedIconSize:{type:Number,default:24},rootIndent:Number,indent:{type:Number,default:32},labelField:{type:String,default:"label"},keyField:{type:String,default:"key"},childrenField:{type:String,default:"children"},disabledField:{type:String,default:"disabled"},defaultExpandAll:Boolean,defaultExpandedKeys:Array,expandedKeys:Array,value:[String,Number],defaultValue:{type:[String,Number],default:null},mode:{type:String,default:"vertical"},watchProps:{type:Array,default:void 0},disabled:Boolean,show:{type:Boolean,default:!0},inverted:Boolean,"onUpdate:expandedKeys":[Function,Array],onUpdateExpandedKeys:[Function,Array],onUpdateValue:[Function,Array],"onUpdate:value":[Function,Array],expandIcon:Function,renderIcon:Function,renderLabel:Function,renderExtra:Function,dropdownProps:Object,accordion:Boolean,nodeProps:Function,dropdownPlacement:{type:String,default:"bottom"},responsive:Boolean,items:Array,onOpenNamesChange:[Function,Array],onSelect:[Function,Array],onExpandedNamesChange:[Function,Array],expandedNames:Array,defaultExpandedNames:Array}),ut=$({name:"Menu",inheritAttrs:!1,props:dt,setup(e){const{mergedClsPrefixRef:r,inlineThemeDisabled:o}=Ie(e),n=Y("Menu","-menu",tt,Yo,e,r),a=j(zo,null),l=y(()=>{var d;const{collapsed:f}=e;if(f!==void 0)return f;if(a){const{collapseModeRef:t,collapsedRef:g}=a;if(t.value==="width")return(d=g.value)!==null&&d!==void 0?d:!1}return!1}),s=y(()=>{const{keyField:d,childrenField:f,disabledField:t}=e;return Ce(e.items||e.options,{getIgnored(g){return we(g)},getChildren(g){return g[f]},getDisabled(g){return g[t]},getKey(g){var k;return(k=g[d])!==null&&k!==void 0?k:g.name}})}),u=y(()=>new Set(s.value.treeNodes.map(d=>d.key))),{watchProps:c}=e,p=E(null);c!=null&&c.includes("defaultValue")?Ne(()=>{p.value=e.defaultValue}):p.value=e.defaultValue;const A=be(e,"value"),w=Oe(A,p),v=E([]),S=()=>{v.value=e.defaultExpandAll?s.value.getNonLeafKeys():e.defaultExpandedNames||e.defaultExpandedKeys||s.value.getPath(w.value,{includeSelf:!1}).keyPath};c!=null&&c.includes("defaultExpandedKeys")?Ne(S):S();const T=Ho(e,["expandedNames","expandedKeys"]),N=Oe(T,v),O=y(()=>s.value.treeNodes),M=y(()=>s.value.getPath(w.value).keyPath);re(ne,{props:e,mergedCollapsedRef:l,mergedThemeRef:n,mergedValueRef:w,mergedExpandedKeysRef:N,activePathRef:M,mergedClsPrefixRef:r,isHorizontalRef:y(()=>e.mode==="horizontal"),invertedRef:be(e,"inverted"),doSelect:Z,toggleExpand:V});function Z(d,f){const{"onUpdate:value":t,onUpdateValue:g,onSelect:k}=e;g&&q(g,d,f),t&&q(t,d,f),k&&q(k,d,f),p.value=d}function F(d){const{"onUpdate:expandedKeys":f,onUpdateExpandedKeys:t,onExpandedNamesChange:g,onOpenNamesChange:k}=e;f&&q(f,d),t&&q(t,d),g&&q(g,d),k&&q(k,d),v.value=d}function V(d){const f=Array.from(N.value),t=f.findIndex(g=>g===d);if(~t)f.splice(t,1);else{if(e.accordion&&u.value.has(d)){const g=f.findIndex(k=>u.value.has(k));g>-1&&f.splice(g,1)}f.push(d)}F(f)}const D=d=>{const f=s.value.getPath(d??w.value,{includeSelf:!1}).keyPath;if(!f.length)return;const t=Array.from(N.value),g=new Set([...t,...f]);e.accordion&&u.value.forEach(k=>{g.has(k)&&!f.includes(k)&&g.delete(k)}),F(Array.from(g))},m=y(()=>{const{inverted:d}=e,{common:{cubicBezierEaseInOut:f},self:t}=n.value,{borderRadius:g,borderColorHorizontal:k,fontSize:Je,itemHeight:Xe,dividerColor:Ze}=t,i={"--n-divider-color":Ze,"--n-bezier":f,"--n-font-size":Je,"--n-border-color-horizontal":k,"--n-border-radius":g,"--n-item-height":Xe};return d?(i["--n-group-text-color"]=t.groupTextColorInverted,i["--n-color"]=t.colorInverted,i["--n-item-text-color"]=t.itemTextColorInverted,i["--n-item-text-color-hover"]=t.itemTextColorHoverInverted,i["--n-item-text-color-active"]=t.itemTextColorActiveInverted,i["--n-item-text-color-child-active"]=t.itemTextColorChildActiveInverted,i["--n-item-text-color-child-active-hover"]=t.itemTextColorChildActiveInverted,i["--n-item-text-color-active-hover"]=t.itemTextColorActiveHoverInverted,i["--n-item-icon-color"]=t.itemIconColorInverted,i["--n-item-icon-color-hover"]=t.itemIconColorHoverInverted,i["--n-item-icon-color-active"]=t.itemIconColorActiveInverted,i["--n-item-icon-color-active-hover"]=t.itemIconColorActiveHoverInverted,i["--n-item-icon-color-child-active"]=t.itemIconColorChildActiveInverted,i["--n-item-icon-color-child-active-hover"]=t.itemIconColorChildActiveHoverInverted,i["--n-item-icon-color-collapsed"]=t.itemIconColorCollapsedInverted,i["--n-item-text-color-horizontal"]=t.itemTextColorHorizontalInverted,i["--n-item-text-color-hover-horizontal"]=t.itemTextColorHoverHorizontalInverted,i["--n-item-text-color-active-horizontal"]=t.itemTextColorActiveHorizontalInverted,i["--n-item-text-color-child-active-horizontal"]=t.itemTextColorChildActiveHorizontalInverted,i["--n-item-text-color-child-active-hover-horizontal"]=t.itemTextColorChildActiveHoverHorizontalInverted,i["--n-item-text-color-active-hover-horizontal"]=t.itemTextColorActiveHoverHorizontalInverted,i["--n-item-icon-color-horizontal"]=t.itemIconColorHorizontalInverted,i["--n-item-icon-color-hover-horizontal"]=t.itemIconColorHoverHorizontalInverted,i["--n-item-icon-color-active-horizontal"]=t.itemIconColorActiveHorizontalInverted,i["--n-item-icon-color-active-hover-horizontal"]=t.itemIconColorActiveHoverHorizontalInverted,i["--n-item-icon-color-child-active-horizontal"]=t.itemIconColorChildActiveHorizontalInverted,i["--n-item-icon-color-child-active-hover-horizontal"]=t.itemIconColorChildActiveHoverHorizontalInverted,i["--n-arrow-color"]=t.arrowColorInverted,i["--n-arrow-color-hover"]=t.arrowColorHoverInverted,i["--n-arrow-color-active"]=t.arrowColorActiveInverted,i["--n-arrow-color-active-hover"]=t.arrowColorActiveHoverInverted,i["--n-arrow-color-child-active"]=t.arrowColorChildActiveInverted,i["--n-arrow-color-child-active-hover"]=t.arrowColorChildActiveHoverInverted,i["--n-item-color-hover"]=t.itemColorHoverInverted,i["--n-item-color-active"]=t.itemColorActiveInverted,i["--n-item-color-active-hover"]=t.itemColorActiveHoverInverted,i["--n-item-color-active-collapsed"]=t.itemColorActiveCollapsedInverted):(i["--n-group-text-color"]=t.groupTextColor,i["--n-color"]=t.color,i["--n-item-text-color"]=t.itemTextColor,i["--n-item-text-color-hover"]=t.itemTextColorHover,i["--n-item-text-color-active"]=t.itemTextColorActive,i["--n-item-text-color-child-active"]=t.itemTextColorChildActive,i["--n-item-text-color-child-active-hover"]=t.itemTextColorChildActiveHover,i["--n-item-text-color-active-hover"]=t.itemTextColorActiveHover,i["--n-item-icon-color"]=t.itemIconColor,i["--n-item-icon-color-hover"]=t.itemIconColorHover,i["--n-item-icon-color-active"]=t.itemIconColorActive,i["--n-item-icon-color-active-hover"]=t.itemIconColorActiveHover,i["--n-item-icon-color-child-active"]=t.itemIconColorChildActive,i["--n-item-icon-color-child-active-hover"]=t.itemIconColorChildActiveHover,i["--n-item-icon-color-collapsed"]=t.itemIconColorCollapsed,i["--n-item-text-color-horizontal"]=t.itemTextColorHorizontal,i["--n-item-text-color-hover-horizontal"]=t.itemTextColorHoverHorizontal,i["--n-item-text-color-active-horizontal"]=t.itemTextColorActiveHorizontal,i["--n-item-text-color-child-active-horizontal"]=t.itemTextColorChildActiveHorizontal,i["--n-item-text-color-child-active-hover-horizontal"]=t.itemTextColorChildActiveHoverHorizontal,i["--n-item-text-color-active-hover-horizontal"]=t.itemTextColorActiveHoverHorizontal,i["--n-item-icon-color-horizontal"]=t.itemIconColorHorizontal,i["--n-item-icon-color-hover-horizontal"]=t.itemIconColorHoverHorizontal,i["--n-item-icon-color-active-horizontal"]=t.itemIconColorActiveHorizontal,i["--n-item-icon-color-active-hover-horizontal"]=t.itemIconColorActiveHoverHorizontal,i["--n-item-icon-color-child-active-horizontal"]=t.itemIconColorChildActiveHorizontal,i["--n-item-icon-color-child-active-hover-horizontal"]=t.itemIconColorChildActiveHoverHorizontal,i["--n-arrow-color"]=t.arrowColor,i["--n-arrow-color-hover"]=t.arrowColorHover,i["--n-arrow-color-active"]=t.arrowColorActive,i["--n-arrow-color-active-hover"]=t.arrowColorActiveHover,i["--n-arrow-color-child-active"]=t.arrowColorChildActive,i["--n-arrow-color-child-active-hover"]=t.arrowColorChildActiveHover,i["--n-item-color-hover"]=t.itemColorHover,i["--n-item-color-active"]=t.itemColorActive,i["--n-item-color-active-hover"]=t.itemColorActiveHover,i["--n-item-color-active-collapsed"]=t.itemColorActiveCollapsed),i}),_=o?ke("menu",y(()=>e.inverted?"a":"b"),m,e):void 0,L=no(),K=E(null),U=E(null);let W=!0;const ee=()=>{var d;W?W=!1:(d=K.value)===null||d===void 0||d.sync({showAllItemsBeforeCalculate:!0})};function ie(){return document.getElementById(L)}const G=E(-1);function se(d){G.value=e.options.length-d}function de(d){d||(G.value=-1)}const ue=y(()=>{const d=G.value;return{children:d===-1?[]:e.options.slice(d)}}),ve=y(()=>{const{childrenField:d,disabledField:f,keyField:t}=e;return Ce([ue.value],{getIgnored(g){return we(g)},getChildren(g){return g[d]},getDisabled(g){return g[f]},getKey(g){var k;return(k=g[t])!==null&&k!==void 0?k:g.name}})}),me=y(()=>Ce([{}]).treeNodes[0]);function he(){var d;if(G.value===-1)return h(_e,{root:!0,level:0,key:"__ellpisisGroupPlaceholder__",internalKey:"__ellpisisGroupPlaceholder__",title:"···",tmNode:me.value,domId:L,isEllipsisPlaceholder:!0});const f=ve.value.treeNodes[0],t=M.value,g=!!(!((d=f.children)===null||d===void 0)&&d.some(k=>t.includes(k.key)));return h(_e,{level:0,root:!0,key:"__ellpisisGroup__",internalKey:"__ellpisisGroup__",title:"···",virtualChildActive:g,tmNode:f,domId:L,rawNodes:f.rawNode.children||[],tmNodes:f.children||[],isEllipsisPlaceholder:!0})}return{mergedClsPrefix:r,controlledExpandedKeys:T,uncontrolledExpanededKeys:v,mergedExpandedKeys:N,uncontrolledValue:p,mergedValue:w,activePath:M,tmNodes:O,mergedTheme:n,mergedCollapsed:l,cssVars:o?void 0:m,themeClass:_==null?void 0:_.themeClass,overflowRef:K,counterRef:U,updateCounter:()=>{},onResize:ee,onUpdateOverflow:de,onUpdateCount:se,renderCounter:he,getCounter:ie,onRender:_==null?void 0:_.onRender,showOption:D,deriveResponsiveState:ee}},render(){const{mergedClsPrefix:e,mode:r,themeClass:o,onRender:n}=this;n==null||n();const a=()=>this.tmNodes.map(c=>Pe(c,this.$props)),s=r==="horizontal"&&this.responsive,u=()=>h("div",io(this.$attrs,{role:r==="horizontal"?"menubar":"menu",class:[`${e}-menu`,o,`${e}-menu--${r}`,s&&`${e}-menu--responsive`,this.mergedCollapsed&&`${e}-menu--collapsed`],style:this.cssVars}),s?h(To,{ref:"overflowRef",onUpdateOverflow:this.onUpdateOverflow,getCounter:this.getCounter,onUpdateCount:this.onUpdateCount,updateCounter:this.updateCounter,style:{width:"100%",display:"flex",overflow:"hidden"}},{default:a,counter:this.renderCounter}):a());return s?h(ro,{onResize:this.onResize},{default:u}):u()}}),vt={xmlns:"http://www.w3.org/2000/svg","xmlns:xlink":"http://www.w3.org/1999/xlink",viewBox:"0 0 512 512"},mt=P("path",{d:"M256 160c16-63.16 76.43-95.41 208-96a15.94 15.94 0 0 1 16 16v288a16 16 0 0 1-16 16c-128 0-177.45 25.81-208 64c-30.37-38-80-64-208-64c-9.88 0-16-8.05-16-17.93V80a15.94 15.94 0 0 1 16-16c131.57.59 192 32.84 208 96z",fill:"none",stroke:"currentColor","stroke-linecap":"round","stroke-linejoin":"round","stroke-width":"32"},null,-1),ht=P("path",{fill:"none",stroke:"currentColor","stroke-linecap":"round","stroke-linejoin":"round","stroke-width":"32",d:"M256 160v288"},null,-1),pt=[mt,ht],ft=$({name:"BookOutline",render:function(r,o){return B(),X("svg",vt,pt)}}),gt={xmlns:"http://www.w3.org/2000/svg","xmlns:xlink":"http://www.w3.org/1999/xlink",viewBox:"0 0 512 512"},Ct=P("path",{d:"M428 224H288a48 48 0 0 1-48-48V36a4 4 0 0 0-4-4h-92a64 64 0 0 0-64 64v320a64 64 0 0 0 64 64h224a64 64 0 0 0 64-64V228a4 4 0 0 0-4-4zm-92 160H176a16 16 0 0 1 0-32h160a16 16 0 0 1 0 32zm0-80H176a16 16 0 0 1 0-32h160a16 16 0 0 1 0 32z",fill:"currentColor"},null,-1),xt=P("path",{d:"M419.22 188.59L275.41 44.78a2 2 0 0 0-3.41 1.41V176a16 16 0 0 0 16 16h129.81a2 2 0 0 0 1.41-3.41z",fill:"currentColor"},null,-1),bt=[Ct,xt],yt=$({name:"DocumentText",render:function(r,o){return B(),X("svg",gt,bt)}}),zt={xmlns:"http://www.w3.org/2000/svg","xmlns:xlink":"http://www.w3.org/1999/xlink",viewBox:"0 0 512 512"},wt=P("path",{fill:"none",stroke:"currentColor","stroke-linecap":"round","stroke-miterlimit":"10","stroke-width":"32",d:"M80 160h352"},null,-1),_t=P("path",{fill:"none",stroke:"currentColor","stroke-linecap":"round","stroke-miterlimit":"10","stroke-width":"32",d:"M80 256h352"},null,-1),It=P("path",{fill:"none",stroke:"currentColor","stroke-linecap":"round","stroke-miterlimit":"10","stroke-width":"32",d:"M80 352h352"},null,-1),kt=[wt,_t,It],Ht=$({name:"MenuOutline",render:function(r,o){return B(),X("svg",zt,kt)}}),At={xmlns:"http://www.w3.org/2000/svg","xmlns:xlink":"http://www.w3.org/1999/xlink",viewBox:"0 0 512 512"},Rt=P("path",{d:"M427.68 351.43C402 320 383.87 304 383.87 217.35C383.87 138 343.35 109.73 310 96c-4.43-1.82-8.6-6-9.95-10.55C294.2 65.54 277.8 48 256 48s-38.21 17.55-44 37.47c-1.35 4.6-5.52 8.71-9.95 10.53c-33.39 13.75-73.87 41.92-73.87 121.35C128.13 304 110 320 84.32 351.43C73.68 364.45 83 384 101.61 384h308.88c18.51 0 27.77-19.61 17.19-32.57z",fill:"none",stroke:"currentColor","stroke-linecap":"round","stroke-linejoin":"round","stroke-width":"32"},null,-1),St=P("path",{d:"M320 384v16a64 64 0 0 1-128 0v-16",fill:"none",stroke:"currentColor","stroke-linecap":"round","stroke-linejoin":"round","stroke-width":"32"},null,-1),Pt=[Rt,St],xe=$({name:"NotificationsOutline",render:function(r,o){return B(),X("svg",At,Pt)}}),Nt={xmlns:"http://www.w3.org/2000/svg","xmlns:xlink":"http://www.w3.org/1999/xlink",viewBox:"0 0 512 512"},$t=P("path",{d:"M259.92 262.91L216.4 149.77a9 9 0 0 0-16.8 0l-43.52 113.14a9 9 0 0 1-5.17 5.17L37.77 311.6a9 9 0 0 0 0 16.8l113.14 43.52a9 9 0 0 1 5.17 5.17l43.52 113.14a9 9 0 0 0 16.8 0l43.52-113.14a9 9 0 0 1 5.17-5.17l113.14-43.52a9 9 0 0 0 0-16.8l-113.14-43.52a9 9 0 0 1-5.17-5.17z",fill:"none",stroke:"currentColor","stroke-linecap":"round","stroke-linejoin":"round","stroke-width":"32"},null,-1),Tt=P("path",{fill:"none",stroke:"currentColor","stroke-linecap":"round","stroke-linejoin":"round","stroke-width":"32",d:"M108 68L88 16L68 68L16 88l52 20l20 52l20-52l52-20l-52-20z"},null,-1),Ot=P("path",{fill:"none",stroke:"currentColor","stroke-linecap":"round","stroke-linejoin":"round","stroke-width":"32",d:"M426.67 117.33L400 48l-26.67 69.33L304 144l69.33 26.67L400 240l26.67-69.33L496 144l-69.33-26.67z"},null,-1),Mt=[$t,Tt,Ot],Lt=$({name:"SparklesOutline",render:function(r,o){return B(),X("svg",Nt,Mt)}}),Et={getChannels:()=>H.get("/notifications/channels"),getChannel:e=>H.get(`/notifications/channels/${e}`),createChannel:e=>H.post("/notifications/channels",e),updateChannel:(e,r)=>H.put(`/notifications/channels/${e}`,r),deleteChannel:e=>H.delete(`/notifications/channels/${e}`),testChannel:e=>H.post(`/notifications/test/${e}`),getHistory:e=>H.get("/notifications/history",{params:e}),deleteHistory:e=>H.delete(`/notifications/history/${e}`),getTypes:()=>H.get("/notifications/types"),getTargetRules:e=>H.get("/notifications/target-rules",{params:e}),createTargetRule:e=>H.post("/notifications/target-rules",e),getTargetRule:e=>H.get(`/notifications/target-rules/${e}`),updateTargetRule:(e,r)=>H.put(`/notifications/target-rules/${e}`,r),deleteTargetRule:e=>H.delete(`/notifications/target-rules/${e}`),toggleTargetRule:e=>H.post(`/notifications/target-rules/${e}/toggle`),getTargets:e=>H.get("/notifications/targets",{params:e}),createTarget:e=>H.post("/notifications/targets",e),getTarget:e=>H.get(`/notifications/targets/${e}`),deleteTarget:e=>H.delete(`/notifications/targets/${e}`),send:e=>H.post("/notifications/send",e),sendAlert:e=>H.post("/notifications/alert",e)},Bt={style:{"font-size":"13px"},class:"mobile-username"},Ft={class:"logo-text"},Kt={style:{"font-size":"13px"}},jt={class:"page"},Vt={__name:"index",setup(e){const r=ao(),o=co(),n=$o(),a=xo(),l=E(!1),s=E(!1),u=E(0),c=y(()=>o.path),p=E([]),A=y(()=>{try{const m=localStorage.getItem("user");if(m)return JSON.parse(m).username||"admin"}catch{}return"admin"});function w(m){return()=>h(m)}const v=[{key:"/dashboard",label:"仪表盘",icon:w(Oo)},{key:"monitoring",label:"监控中心",icon:w(Te),children:[{key:"/monitoring/devices",label:"设备监控"},{key:"/monitoring/alerts",label:"告警管理"},{key:"/monitoring/performance",label:"性能监控"}]},{key:"workorder",label:"工单管理",icon:w(Eo),children:[{key:"/workorder/list",label:"工单列表"},{key:"/workorder/create",label:"创建工单"},{key:"/workorder/my",label:"我的工单"}]},{key:"knowledge",label:"知识库",icon:w(ft),children:[{key:"/knowledge/list",label:"知识文档"},{key:"/knowledge/category",label:"分类管理"}]},{key:"ai",label:"AI助手",icon:w(Lt),children:[{key:"/ai/copilot",label:"智能问答"},{key:"/ai/analyze",label:"智能分析"}]},{key:"automation",label:"自动化",icon:w(Mo),children:[{key:"/automation/script",label:"脚本管理"},{key:"/automation/task",label:"任务调度"},{key:"/automation/execute",label:"执行记录"}]},{key:"backup",label:"备份管理",icon:w(yt),children:[{key:"/backup/list",label:"备份记录"},{key:"/backup/restore",label:"恢复管理"}]},{key:"notification",label:"消息中心",icon:w(xe),children:[{key:"/notification/message",label:"我的消息"},{key:"/notification/config",label:"通知配置"}]},{key:"system",label:"系统管理",icon:w(Lo),children:[{key:"/system/user",label:"用户管理"},{key:"/system/role",label:"角色管理"},{key:"/system/menu",label:"菜单管理"},{key:"/system/dict",label:"字典管理"},{key:"/system/config",label:"参数配置"},{key:"/system/logs",label:"日志查看"},{key:"/system/adapters",label:"适配器管理"}]}],S=y(()=>{const m=[];return o.matched.forEach(_=>{_.meta.title&&m.push(_.meta.title)}),m.length?m:["仪表盘"]});function T(){r.push("/dashboard")}function N(){l.value=!l.value}function O(m,_){_.children===void 0&&r.push(m)}function M(m){p.value=m.length>0?[m[m.length-1]]:[]}const Z=[{label:"个人中心",key:"profile"},{label:"修改密码",key:"password"},{type:"divider",key:"d1"},{label:"退出登录",key:"logout"}];function F(m){m==="logout"?a.warning({title:"退出确认",content:"确定要退出登录吗？",positiveText:"确定",negativeText:"取消",onPositiveClick:()=>{localStorage.removeItem("token"),localStorage.removeItem("user"),n.success("已退出登录"),r.push("/login")}}):m==="password"?n.info("修改密码功能开发中"):m==="profile"&&n.info("个人中心功能开发中")}const V=async()=>{try{const m=await Et.getHistory({page:1,page_size:1});u.value=(m==null?void 0:m.total)||(Array.isArray(m)?m.length:0)}catch(m){console.warn("Failed to fetch notification count:",m)}},D=()=>{s.value=window.innerWidth<768,s.value&&(l.value=!0)};return Be(()=>{D(),window.addEventListener("resize",D),V();const m=setInterval(V,6e4);ye(()=>clearInterval(m))}),lo(()=>o.path,()=>{const m=v.find(_=>{var L;return(L=_.children)==null?void 0:L.some(K=>K.key===o.path)});m&&(p.value=[m.key])},{immediate:!0}),ye(()=>{window.removeEventListener("resize",D)}),(m,_)=>{const L=Bo,K=uo,U=Ao,W=Ro,ee=_o,ie=Ke,G=ot,se=ut,de=Io,ue=Xo,ve=Go,me=so("router-view"),he=ko,d=wo;return B(),$e(d,{"has-sider":"",class:"layout","native-scrollbar":!1},{default:I(()=>[z(G,{class:"mobile-header"},{default:I(()=>[z(U,{align:"center"},{default:I(()=>[z(K,{quaternary:"",circle:"",size:"small",onClick:N},{icon:I(()=>[z(L,null,{default:I(()=>[z(le(Ht))]),_:1})]),_:1}),_[3]||(_[3]=P("span",{class:"mobile-title"},"ITOps",-1))]),_:1}),z(U,{align:"center"},{default:I(()=>[z(W,{value:u.value,max:99,show:u.value>0},{default:I(()=>[z(K,{quaternary:"",circle:"",size:"small",onClick:_[0]||(_[0]=f=>m.$router.push("/notification/message"))},{icon:I(()=>[z(L,null,{default:I(()=>[z(le(xe))]),_:1})]),_:1})]),_:1},8,["value","show"]),z(ie,{options:Z,onSelect:F},{default:I(()=>[z(U,{align:"center",style:{cursor:"pointer",padding:"0 8px"}},{default:I(()=>[z(ee,{round:"",size:"small",style:{background:"#18a058"}},{default:I(()=>[ge(te(A.value.charAt(0).toUpperCase()),1)]),_:1}),P("span",Bt,te(A.value),1)]),_:1})]),_:1})]),_:1})]),_:1}),z(de,{bordered:"",collapsed:l.value,"collapsed-width":64,width:220,"show-trigger":"bar","collapse-mode":"width","native-scrollbar":!1,class:mo(["sider",{"mobile-sider":s.value}]),style:vo(s.value&&!l.value?{position:"fixed",left:0,top:0,bottom:0,zIndex:1e3,transform:"translateX(-100%)",transition:"transform 0.3s"}:{})},{default:I(()=>[s.value&&!l.value?(B(),X("div",{key:0,class:"sidebar-overlay",onClick:_[1]||(_[1]=f=>l.value=!0)})):ho("",!0),P("div",{class:"logo",onClick:T},[z(L,{size:"26",color:"#18a058"},{default:I(()=>[z(le(Te))]),_:1}),po(P("span",Ft,"ITOps",512),[[fo,!l.value]])]),z(se,{collapsed:l.value,"collapsed-width":64,"collapsed-icon-size":22,options:v,value:c.value,"expanded-keys":p.value,indent:16,"onUpdate:value":O,"onUpdate:expandedKeys":M},null,8,["collapsed","value","expanded-keys"])]),_:1},8,["collapsed","class","style"]),z(d,{class:"main"},{default:I(()=>[z(G,{class:"header"},{default:I(()=>[z(ve,null,{default:I(()=>[(B(!0),X(Fe,null,go(S.value,f=>(B(),$e(ue,{key:f},{default:I(()=>[ge(te(f),1)]),_:2},1024))),128))]),_:1}),z(U,{align:"center",class:"desktop-only"},{default:I(()=>[z(W,{value:u.value,max:99,show:u.value>0},{default:I(()=>[z(K,{quaternary:"",circle:"",size:"small",onClick:_[2]||(_[2]=f=>m.$router.push("/notification/message"))},{icon:I(()=>[z(L,null,{default:I(()=>[z(le(xe))]),_:1})]),_:1})]),_:1},8,["value","show"]),z(ie,{options:Z,onSelect:F},{default:I(()=>[z(U,{align:"center",style:{cursor:"pointer",padding:"0 8px"}},{default:I(()=>[z(ee,{round:"",size:"small",style:{background:"#18a058"}},{default:I(()=>[ge(te(A.value.charAt(0).toUpperCase()),1)]),_:1}),P("span",Kt,te(A.value),1)]),_:1})]),_:1})]),_:1})]),_:1}),z(he,{class:"content","native-scrollbar":!1},{default:I(()=>[P("div",jt,[z(me)])]),_:1})]),_:1})]),_:1})}}},ar=Co(Vt,[["__scopeId","data-v-b34f29a3"]]);export{ar as default};
