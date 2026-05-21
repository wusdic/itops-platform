import{l as de,I as a,m as he,p as z,q as B,J as H,n as R,j as N,ai as D,k as I,aY as ge,s as K,v as w,av as J,x as pe,i as ue,W as be,y as L,ad as p,b1 as Ce,aC as V,z as ve,A as fe,C as me,E as xe,aK as ke,br as ye,bs as Se,b3 as A}from"./index-CQozwhl-.js";function ze(e,t="default",l=[]){const o=e.$slots[t];return o===void 0?l:o()}const Ie={closeIconSizeTiny:"12px",closeIconSizeSmall:"12px",closeIconSizeMedium:"14px",closeIconSizeLarge:"14px",closeSizeTiny:"16px",closeSizeSmall:"16px",closeSizeMedium:"18px",closeSizeLarge:"18px",padding:"0 7px",closeMargin:"0 0 0 4px"};function Pe(e){const{textColor2:t,primaryColorHover:l,primaryColorPressed:u,primaryColor:o,infoColor:c,successColor:i,warningColor:n,errorColor:d,baseColor:m,borderColor:x,opacityDisabled:h,tagColor:v,closeIconColor:r,closeIconColorHover:s,closeIconColorPressed:b,borderRadiusSmall:g,fontSizeMini:y,fontSizeTiny:f,fontSizeSmall:k,fontSizeMedium:S,heightMini:P,heightTiny:C,heightSmall:M,heightMedium:_,closeColorHover:E,closeColorPressed:T,buttonColor2Hover:j,buttonColor2Pressed:W,fontWeightStrong:O}=e;return Object.assign(Object.assign({},Ie),{closeBorderRadius:g,heightTiny:P,heightSmall:C,heightMedium:M,heightLarge:_,borderRadius:g,opacityDisabled:h,fontSizeTiny:y,fontSizeSmall:f,fontSizeMedium:k,fontSizeLarge:S,fontWeightStrong:O,textColorCheckable:t,textColorHoverCheckable:t,textColorPressedCheckable:t,textColorChecked:m,colorCheckable:"#0000",colorHoverCheckable:j,colorPressedCheckable:W,colorChecked:o,colorCheckedHover:l,colorCheckedPressed:u,border:`1px solid ${x}`,textColor:t,color:v,colorBordered:"rgb(250, 250, 252)",closeIconColor:r,closeIconColorHover:s,closeIconColorPressed:b,closeColorHover:E,closeColorPressed:T,borderPrimary:`1px solid ${a(o,{alpha:.3})}`,textColorPrimary:o,colorPrimary:a(o,{alpha:.12}),colorBorderedPrimary:a(o,{alpha:.1}),closeIconColorPrimary:o,closeIconColorHoverPrimary:o,closeIconColorPressedPrimary:o,closeColorHoverPrimary:a(o,{alpha:.12}),closeColorPressedPrimary:a(o,{alpha:.18}),borderInfo:`1px solid ${a(c,{alpha:.3})}`,textColorInfo:c,colorInfo:a(c,{alpha:.12}),colorBorderedInfo:a(c,{alpha:.1}),closeIconColorInfo:c,closeIconColorHoverInfo:c,closeIconColorPressedInfo:c,closeColorHoverInfo:a(c,{alpha:.12}),closeColorPressedInfo:a(c,{alpha:.18}),borderSuccess:`1px solid ${a(i,{alpha:.3})}`,textColorSuccess:i,colorSuccess:a(i,{alpha:.12}),colorBorderedSuccess:a(i,{alpha:.1}),closeIconColorSuccess:i,closeIconColorHoverSuccess:i,closeIconColorPressedSuccess:i,closeColorHoverSuccess:a(i,{alpha:.12}),closeColorPressedSuccess:a(i,{alpha:.18}),borderWarning:`1px solid ${a(n,{alpha:.35})}`,textColorWarning:n,colorWarning:a(n,{alpha:.15}),colorBorderedWarning:a(n,{alpha:.12}),closeIconColorWarning:n,closeIconColorHoverWarning:n,closeIconColorPressedWarning:n,closeColorHoverWarning:a(n,{alpha:.12}),closeColorPressedWarning:a(n,{alpha:.18}),borderError:`1px solid ${a(d,{alpha:.23})}`,textColorError:d,colorError:a(d,{alpha:.1}),colorBorderedError:a(d,{alpha:.08}),closeIconColorError:d,closeIconColorHoverError:d,closeIconColorPressedError:d,closeColorHoverError:a(d,{alpha:.12}),closeColorPressedError:a(d,{alpha:.18})})}const Be={common:de,self:Pe},$e={color:Object,type:{type:String,default:"default"},round:Boolean,size:{type:String,default:"medium"},closable:Boolean,disabled:{type:Boolean,default:void 0}},He=he("tag",`
 --n-close-margin: var(--n-close-margin-top) var(--n-close-margin-right) var(--n-close-margin-bottom) var(--n-close-margin-left);
 white-space: nowrap;
 position: relative;
 box-sizing: border-box;
 cursor: default;
 display: inline-flex;
 align-items: center;
 flex-wrap: nowrap;
 padding: var(--n-padding);
 border-radius: var(--n-border-radius);
 color: var(--n-text-color);
 background-color: var(--n-color);
 transition: 
 border-color .3s var(--n-bezier),
 background-color .3s var(--n-bezier),
 color .3s var(--n-bezier),
 box-shadow .3s var(--n-bezier),
 opacity .3s var(--n-bezier);
 line-height: 1;
 height: var(--n-height);
 font-size: var(--n-font-size);
`,[z("strong",`
 font-weight: var(--n-font-weight-strong);
 `),B("border",`
 pointer-events: none;
 position: absolute;
 left: 0;
 right: 0;
 top: 0;
 bottom: 0;
 border-radius: inherit;
 border: var(--n-border);
 transition: border-color .3s var(--n-bezier);
 `),B("icon",`
 display: flex;
 margin: 0 4px 0 0;
 color: var(--n-text-color);
 transition: color .3s var(--n-bezier);
 font-size: var(--n-avatar-size-override);
 `),B("avatar",`
 display: flex;
 margin: 0 6px 0 0;
 `),B("close",`
 margin: var(--n-close-margin);
 transition:
 background-color .3s var(--n-bezier),
 color .3s var(--n-bezier);
 `),z("round",`
 padding: 0 calc(var(--n-height) / 3);
 border-radius: calc(var(--n-height) / 2);
 `,[B("icon",`
 margin: 0 4px 0 calc((var(--n-height) - 8px) / -2);
 `),B("avatar",`
 margin: 0 6px 0 calc((var(--n-height) - 8px) / -2);
 `),z("closable",`
 padding: 0 calc(var(--n-height) / 4) 0 calc(var(--n-height) / 3);
 `)]),z("icon, avatar",[z("round",`
 padding: 0 calc(var(--n-height) / 3) 0 calc(var(--n-height) / 2);
 `)]),z("disabled",`
 cursor: not-allowed !important;
 opacity: var(--n-opacity-disabled);
 `),z("checkable",`
 cursor: pointer;
 box-shadow: none;
 color: var(--n-text-color-checkable);
 background-color: var(--n-color-checkable);
 `,[H("disabled",[R("&:hover","background-color: var(--n-color-hover-checkable);",[H("checked","color: var(--n-text-color-hover-checkable);")]),R("&:active","background-color: var(--n-color-pressed-checkable);",[H("checked","color: var(--n-text-color-pressed-checkable);")])]),z("checked",`
 color: var(--n-text-color-checked);
 background-color: var(--n-color-checked);
 `,[H("disabled",[R("&:hover","background-color: var(--n-color-checked-hover);"),R("&:active","background-color: var(--n-color-checked-pressed);")])])])]),Re=Object.assign(Object.assign(Object.assign({},w.props),$e),{bordered:{type:Boolean,default:void 0},checked:Boolean,checkable:Boolean,strong:Boolean,triggerClickOnClose:Boolean,onClose:[Array,Function],onMouseenter:Function,onMouseleave:Function,"onUpdate:checked":Function,onUpdateChecked:Function,internalCloseFocusable:{type:Boolean,default:!0},internalCloseIsButtonTag:{type:Boolean,default:!0},onCheckedChange:Function}),we=ve("n-tag"),Oe=N({name:"Tag",props:Re,slots:Object,setup(e){const t=ue(null),{mergedBorderedRef:l,mergedClsPrefixRef:u,inlineThemeDisabled:o,mergedRtlRef:c}=K(e),i=w("Tag","-tag",He,Be,e,u);fe(we,{roundRef:me(e,"round")});function n(){if(!e.disabled&&e.checkable){const{checked:r,onCheckedChange:s,onUpdateChecked:b,"onUpdate:checked":g}=e;b&&b(!r),g&&g(!r),s&&s(!r)}}function d(r){if(e.triggerClickOnClose||r.stopPropagation(),!e.disabled){const{onClose:s}=e;s&&be(s,r)}}const m={setTextContent(r){const{value:s}=t;s&&(s.textContent=r)}},x=J("Tag",c,u),h=L(()=>{const{type:r,size:s,color:{color:b,textColor:g}={}}=e,{common:{cubicBezierEaseInOut:y},self:{padding:f,closeMargin:k,borderRadius:S,opacityDisabled:P,textColorCheckable:C,textColorHoverCheckable:M,textColorPressedCheckable:_,textColorChecked:E,colorCheckable:T,colorHoverCheckable:j,colorPressedCheckable:W,colorChecked:O,colorCheckedHover:q,colorCheckedPressed:Y,closeBorderRadius:Q,fontWeightStrong:X,[p("colorBordered",r)]:Z,[p("closeSize",s)]:ee,[p("closeIconSize",s)]:oe,[p("fontSize",s)]:re,[p("height",s)]:G,[p("color",r)]:le,[p("textColor",r)]:ae,[p("border",r)]:ne,[p("closeIconColor",r)]:U,[p("closeIconColorHover",r)]:te,[p("closeIconColorPressed",r)]:ce,[p("closeColorHover",r)]:se,[p("closeColorPressed",r)]:ie}}=i.value,$=Ce(k);return{"--n-font-weight-strong":X,"--n-avatar-size-override":`calc(${G} - 8px)`,"--n-bezier":y,"--n-border-radius":S,"--n-border":ne,"--n-close-icon-size":oe,"--n-close-color-pressed":ie,"--n-close-color-hover":se,"--n-close-border-radius":Q,"--n-close-icon-color":U,"--n-close-icon-color-hover":te,"--n-close-icon-color-pressed":ce,"--n-close-icon-color-disabled":U,"--n-close-margin-top":$.top,"--n-close-margin-right":$.right,"--n-close-margin-bottom":$.bottom,"--n-close-margin-left":$.left,"--n-close-size":ee,"--n-color":b||(l.value?Z:le),"--n-color-checkable":T,"--n-color-checked":O,"--n-color-checked-hover":q,"--n-color-checked-pressed":Y,"--n-color-hover-checkable":j,"--n-color-pressed-checkable":W,"--n-font-size":re,"--n-height":G,"--n-opacity-disabled":P,"--n-padding":f,"--n-text-color":g||ae,"--n-text-color-checkable":C,"--n-text-color-checked":E,"--n-text-color-hover-checkable":M,"--n-text-color-pressed-checkable":_}}),v=o?pe("tag",L(()=>{let r="";const{type:s,size:b,color:{color:g,textColor:y}={}}=e;return r+=s[0],r+=b[0],g&&(r+=`a${V(g)}`),y&&(r+=`b${V(y)}`),l.value&&(r+="c"),r}),h,e):void 0;return Object.assign(Object.assign({},m),{rtlEnabled:x,mergedClsPrefix:u,contentRef:t,mergedBordered:l,handleClick:n,handleCloseClick:d,cssVars:o?void 0:h,themeClass:v==null?void 0:v.themeClass,onRender:v==null?void 0:v.onRender})},render(){var e,t;const{mergedClsPrefix:l,rtlEnabled:u,closable:o,color:{borderColor:c}={},round:i,onRender:n,$slots:d}=this;n==null||n();const m=D(d.avatar,h=>h&&I("div",{class:`${l}-tag__avatar`},h)),x=D(d.icon,h=>h&&I("div",{class:`${l}-tag__icon`},h));return I("div",{class:[`${l}-tag`,this.themeClass,{[`${l}-tag--rtl`]:u,[`${l}-tag--strong`]:this.strong,[`${l}-tag--disabled`]:this.disabled,[`${l}-tag--checkable`]:this.checkable,[`${l}-tag--checked`]:this.checkable&&this.checked,[`${l}-tag--round`]:i,[`${l}-tag--avatar`]:m,[`${l}-tag--icon`]:x,[`${l}-tag--closable`]:o}],style:this.cssVars,onClick:this.handleClick,onMouseenter:this.onMouseenter,onMouseleave:this.onMouseleave},x||m,I("span",{class:`${l}-tag__content`,ref:"contentRef"},(t=(e=this.$slots).default)===null||t===void 0?void 0:t.call(e)),!this.checkable&&o?I(ge,{clsPrefix:l,class:`${l}-tag__close`,disabled:this.disabled,onClick:this.handleCloseClick,focusable:this.internalCloseFocusable,round:i,isButtonTag:this.internalCloseIsButtonTag,absolute:!0}):null,!this.checkable&&this.mergedBordered?I("div",{class:`${l}-tag__border`,style:{borderColor:c}}):null)}}),Me={gapSmall:"4px 8px",gapMedium:"8px 12px",gapLarge:"12px 16px"};function _e(){return Me}const Ee={self:_e};let F;function Te(){if(!xe)return!0;if(F===void 0){const e=document.createElement("div");e.style.display="flex",e.style.flexDirection="column",e.style.rowGap="1px",e.appendChild(document.createElement("div")),e.appendChild(document.createElement("div")),document.body.appendChild(e);const t=e.scrollHeight===1;return document.body.removeChild(e),F=t}return F}const je=Object.assign(Object.assign({},w.props),{align:String,justify:{type:String,default:"start"},inline:Boolean,vertical:Boolean,reverse:Boolean,size:{type:[String,Number,Array],default:"medium"},wrapItem:{type:Boolean,default:!0},itemClass:String,itemStyle:[String,Object],wrap:{type:Boolean,default:!0},internalUseGap:{type:Boolean,default:void 0}}),Fe=N({name:"Space",props:je,setup(e){const{mergedClsPrefixRef:t,mergedRtlRef:l}=K(e),u=w("Space","-space",void 0,Ee,e,t),o=J("Space",l,t);return{useGap:Te(),rtlEnabled:o,mergedClsPrefix:t,margin:L(()=>{const{size:c}=e;if(Array.isArray(c))return{horizontal:c[0],vertical:c[1]};if(typeof c=="number")return{horizontal:c,vertical:c};const{self:{[p("gap",c)]:i}}=u.value,{row:n,col:d}=Se(i);return{horizontal:A(d),vertical:A(n)}})}},render(){const{vertical:e,reverse:t,align:l,inline:u,justify:o,itemClass:c,itemStyle:i,margin:n,wrap:d,mergedClsPrefix:m,rtlEnabled:x,useGap:h,wrapItem:v,internalUseGap:r}=this,s=ke(ze(this),!1);if(!s.length)return null;const b=`${n.horizontal}px`,g=`${n.horizontal/2}px`,y=`${n.vertical}px`,f=`${n.vertical/2}px`,k=s.length-1,S=o.startsWith("space-");return I("div",{role:"none",class:[`${m}-space`,x&&`${m}-space--rtl`],style:{display:u?"inline-flex":"flex",flexDirection:e&&!t?"column":e&&t?"column-reverse":!e&&t?"row-reverse":"row",justifyContent:["start","end"].includes(o)?`flex-${o}`:o,flexWrap:!d||e?"nowrap":"wrap",marginTop:h||e?"":`-${f}`,marginBottom:h||e?"":`-${f}`,alignItems:l,gap:h?`${n.vertical}px ${n.horizontal}px`:""}},!v&&(h||r)?s:s.map((P,C)=>P.type===ye?P:I("div",{role:"none",class:c,style:[i,{maxWidth:"100%"},h?"":e?{marginBottom:C!==k?y:""}:x?{marginLeft:S?o==="space-between"&&C===k?"":g:C!==k?b:"",marginRight:S?o==="space-between"&&C===0?"":g:"",paddingTop:f,paddingBottom:f}:{marginRight:S?o==="space-between"&&C===k?"":g:C!==k?b:"",marginLeft:S?o==="space-between"&&C===0?"":g:"",paddingTop:f,paddingBottom:f}]},P)))}});export{Fe as _,Oe as a,ze as g,we as t};
