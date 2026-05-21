import{l as ae,I as O,m as B,p as x,q as s,n as S,J as E,F as ie,aj as N,i as F,O as M,s as j,W as I,z as de,C as U,j as G,k as y,ai as se,v as V,av as L,x as K,y as _,ad as D,aK as le,A as ce}from"./index-BqCB-C5P.js";import{u as W}from"./get-Czfyc8y4.js";import{g as ue}from"./Space-BTkNb7QO.js";const be={radioSizeSmall:"14px",radioSizeMedium:"16px",radioSizeLarge:"18px",labelPadding:"0 8px",labelFontWeight:"400"};function he(o){const{borderColor:e,primaryColor:t,baseColor:a,textColorDisabled:r,inputColorDisabled:l,textColor2:d,opacityDisabled:c,borderRadius:i,fontSizeSmall:f,fontSizeMedium:g,fontSizeLarge:C,heightSmall:h,heightMedium:R,heightLarge:m,lineHeight:w}=o;return Object.assign(Object.assign({},be),{labelLineHeight:w,buttonHeightSmall:h,buttonHeightMedium:R,buttonHeightLarge:m,fontSizeSmall:f,fontSizeMedium:g,fontSizeLarge:C,boxShadow:`inset 0 0 0 1px ${e}`,boxShadowActive:`inset 0 0 0 1px ${t}`,boxShadowFocus:`inset 0 0 0 1px ${t}, 0 0 0 2px ${O(t,{alpha:.2})}`,boxShadowHover:`inset 0 0 0 1px ${t}`,boxShadowDisabled:`inset 0 0 0 1px ${e}`,color:a,colorDisabled:l,colorActive:"#0000",textColor:d,textColorDisabled:r,dotColorActive:t,dotColorDisabled:e,buttonBorderColor:e,buttonBorderColorActive:t,buttonBorderColorHover:e,buttonColor:a,buttonColorActive:a,buttonTextColor:d,buttonTextColorActive:t,buttonTextColorHover:t,opacityDisabled:c,buttonBoxShadowFocus:`inset 0 0 0 1px ${t}, 0 0 0 2px ${O(t,{alpha:.3})}`,buttonBoxShadowHover:"inset 0 0 0 1px #0000",buttonBoxShadow:"inset 0 0 0 1px #0000",buttonBorderRadius:i})}const q={name:"Radio",common:ae,self:he},ve=B("radio",`
 line-height: var(--n-label-line-height);
 outline: none;
 position: relative;
 user-select: none;
 -webkit-user-select: none;
 display: inline-flex;
 align-items: flex-start;
 flex-wrap: nowrap;
 font-size: var(--n-font-size);
 word-break: break-word;
`,[x("checked",[s("dot",`
 background-color: var(--n-color-active);
 `)]),s("dot-wrapper",`
 position: relative;
 flex-shrink: 0;
 flex-grow: 0;
 width: var(--n-radio-size);
 `),B("radio-input",`
 position: absolute;
 border: 0;
 width: 0;
 height: 0;
 opacity: 0;
 margin: 0;
 `),s("dot",`
 position: absolute;
 top: 50%;
 left: 0;
 transform: translateY(-50%);
 height: var(--n-radio-size);
 width: var(--n-radio-size);
 background: var(--n-color);
 box-shadow: var(--n-box-shadow);
 border-radius: 50%;
 transition:
 background-color .3s var(--n-bezier),
 box-shadow .3s var(--n-bezier);
 `,[S("&::before",`
 content: "";
 opacity: 0;
 position: absolute;
 left: 4px;
 top: 4px;
 height: calc(100% - 8px);
 width: calc(100% - 8px);
 border-radius: 50%;
 transform: scale(.8);
 background: var(--n-dot-color-active);
 transition: 
 opacity .3s var(--n-bezier),
 background-color .3s var(--n-bezier),
 transform .3s var(--n-bezier);
 `),x("checked",{boxShadow:"var(--n-box-shadow-active)"},[S("&::before",`
 opacity: 1;
 transform: scale(1);
 `)])]),s("label",`
 color: var(--n-text-color);
 padding: var(--n-label-padding);
 font-weight: var(--n-label-font-weight);
 display: inline-block;
 transition: color .3s var(--n-bezier);
 `),E("disabled",`
 cursor: pointer;
 `,[S("&:hover",[s("dot",{boxShadow:"var(--n-box-shadow-hover)"})]),x("focus",[S("&:not(:active)",[s("dot",{boxShadow:"var(--n-box-shadow-focus)"})])])]),x("disabled",`
 cursor: not-allowed;
 `,[s("dot",{boxShadow:"var(--n-box-shadow-disabled)",backgroundColor:"var(--n-color-disabled)"},[S("&::before",{backgroundColor:"var(--n-dot-color-disabled)"}),x("checked",`
 opacity: 1;
 `)]),s("label",{color:"var(--n-text-color-disabled)"}),B("radio-input",`
 cursor: not-allowed;
 `)])]),fe={name:String,value:{type:[String,Number,Boolean],default:"on"},checked:{type:Boolean,default:void 0},defaultChecked:Boolean,disabled:{type:Boolean,default:void 0},label:String,size:String,onUpdateChecked:[Function,Array],"onUpdate:checked":[Function,Array],checkedValue:{type:Boolean,default:void 0}},J=de("n-radio-group");function ge(o){const e=ie(J,null),t=N(o,{mergedSize(n){const{size:u}=o;if(u!==void 0)return u;if(e){const{mergedSizeRef:{value:v}}=e;if(v!==void 0)return v}return n?n.mergedSize.value:"medium"},mergedDisabled(n){return!!(o.disabled||e!=null&&e.disabledRef.value||n!=null&&n.disabled.value)}}),{mergedSizeRef:a,mergedDisabledRef:r}=t,l=F(null),d=F(null),c=F(o.defaultChecked),i=U(o,"checked"),f=W(i,c),g=M(()=>e?e.valueRef.value===o.value:f.value),C=M(()=>{const{name:n}=o;if(n!==void 0)return n;if(e)return e.nameRef.value}),h=F(!1);function R(){if(e){const{doUpdateValue:n}=e,{value:u}=o;I(n,u)}else{const{onUpdateChecked:n,"onUpdate:checked":u}=o,{nTriggerFormInput:v,nTriggerFormChange:b}=t;n&&I(n,!0),u&&I(u,!0),v(),b(),c.value=!0}}function m(){r.value||g.value||R()}function w(){m(),l.value&&(l.value.checked=g.value)}function z(){h.value=!1}function k(){h.value=!0}return{mergedClsPrefix:e?e.mergedClsPrefixRef:j(o).mergedClsPrefixRef,inputRef:l,labelRef:d,mergedName:C,mergedDisabled:r,renderSafeChecked:g,focus:h,mergedSize:a,handleRadioInputChange:w,handleRadioInputBlur:z,handleRadioInputFocus:k}}const pe=Object.assign(Object.assign({},V.props),fe),ze=G({name:"Radio",props:pe,setup(o){const e=ge(o),t=V("Radio","-radio",ve,q,o,e.mergedClsPrefix),a=_(()=>{const{mergedSize:{value:f}}=e,{common:{cubicBezierEaseInOut:g},self:{boxShadow:C,boxShadowActive:h,boxShadowDisabled:R,boxShadowFocus:m,boxShadowHover:w,color:z,colorDisabled:k,colorActive:n,textColor:u,textColorDisabled:v,dotColorActive:b,dotColorDisabled:p,labelPadding:$,labelLineHeight:A,labelFontWeight:T,[D("fontSize",f)]:H,[D("radioSize",f)]:P}}=t.value;return{"--n-bezier":g,"--n-label-line-height":A,"--n-label-font-weight":T,"--n-box-shadow":C,"--n-box-shadow-active":h,"--n-box-shadow-disabled":R,"--n-box-shadow-focus":m,"--n-box-shadow-hover":w,"--n-color":z,"--n-color-active":n,"--n-color-disabled":k,"--n-dot-color-active":b,"--n-dot-color-disabled":p,"--n-font-size":H,"--n-radio-size":P,"--n-text-color":u,"--n-text-color-disabled":v,"--n-label-padding":$}}),{inlineThemeDisabled:r,mergedClsPrefixRef:l,mergedRtlRef:d}=j(o),c=L("Radio",d,l),i=r?K("radio",_(()=>e.mergedSize.value[0]),a,o):void 0;return Object.assign(e,{rtlEnabled:c,cssVars:r?void 0:a,themeClass:i==null?void 0:i.themeClass,onRender:i==null?void 0:i.onRender})},render(){const{$slots:o,mergedClsPrefix:e,onRender:t,label:a}=this;return t==null||t(),y("label",{class:[`${e}-radio`,this.themeClass,this.rtlEnabled&&`${e}-radio--rtl`,this.mergedDisabled&&`${e}-radio--disabled`,this.renderSafeChecked&&`${e}-radio--checked`,this.focus&&`${e}-radio--focus`],style:this.cssVars},y("div",{class:`${e}-radio__dot-wrapper`}," ",y("div",{class:[`${e}-radio__dot`,this.renderSafeChecked&&`${e}-radio__dot--checked`]}),y("input",{ref:"inputRef",type:"radio",class:`${e}-radio-input`,value:this.value,name:this.mergedName,checked:this.renderSafeChecked,disabled:this.mergedDisabled,onChange:this.handleRadioInputChange,onFocus:this.handleRadioInputFocus,onBlur:this.handleRadioInputBlur})),se(o.default,r=>!r&&!a?null:y("div",{ref:"labelRef",class:`${e}-radio__label`},r||a)))}}),me=B("radio-group",`
 display: inline-block;
 font-size: var(--n-font-size);
`,[s("splitor",`
 display: inline-block;
 vertical-align: bottom;
 width: 1px;
 transition:
 background-color .3s var(--n-bezier),
 opacity .3s var(--n-bezier);
 background: var(--n-button-border-color);
 `,[x("checked",{backgroundColor:"var(--n-button-border-color-active)"}),x("disabled",{opacity:"var(--n-opacity-disabled)"})]),x("button-group",`
 white-space: nowrap;
 height: var(--n-height);
 line-height: var(--n-height);
 `,[B("radio-button",{height:"var(--n-height)",lineHeight:"var(--n-height)"}),s("splitor",{height:"var(--n-height)"})]),B("radio-button",`
 vertical-align: bottom;
 outline: none;
 position: relative;
 user-select: none;
 -webkit-user-select: none;
 display: inline-block;
 box-sizing: border-box;
 padding-left: 14px;
 padding-right: 14px;
 white-space: nowrap;
 transition:
 background-color .3s var(--n-bezier),
 opacity .3s var(--n-bezier),
 border-color .3s var(--n-bezier),
 color .3s var(--n-bezier);
 background: var(--n-button-color);
 color: var(--n-button-text-color);
 border-top: 1px solid var(--n-button-border-color);
 border-bottom: 1px solid var(--n-button-border-color);
 `,[B("radio-input",`
 pointer-events: none;
 position: absolute;
 border: 0;
 border-radius: inherit;
 left: 0;
 right: 0;
 top: 0;
 bottom: 0;
 opacity: 0;
 z-index: 1;
 `),s("state-border",`
 z-index: 1;
 pointer-events: none;
 position: absolute;
 box-shadow: var(--n-button-box-shadow);
 transition: box-shadow .3s var(--n-bezier);
 left: -1px;
 bottom: -1px;
 right: -1px;
 top: -1px;
 `),S("&:first-child",`
 border-top-left-radius: var(--n-button-border-radius);
 border-bottom-left-radius: var(--n-button-border-radius);
 border-left: 1px solid var(--n-button-border-color);
 `,[s("state-border",`
 border-top-left-radius: var(--n-button-border-radius);
 border-bottom-left-radius: var(--n-button-border-radius);
 `)]),S("&:last-child",`
 border-top-right-radius: var(--n-button-border-radius);
 border-bottom-right-radius: var(--n-button-border-radius);
 border-right: 1px solid var(--n-button-border-color);
 `,[s("state-border",`
 border-top-right-radius: var(--n-button-border-radius);
 border-bottom-right-radius: var(--n-button-border-radius);
 `)]),E("disabled",`
 cursor: pointer;
 `,[S("&:hover",[s("state-border",`
 transition: box-shadow .3s var(--n-bezier);
 box-shadow: var(--n-button-box-shadow-hover);
 `),E("checked",{color:"var(--n-button-text-color-hover)"})]),x("focus",[S("&:not(:active)",[s("state-border",{boxShadow:"var(--n-button-box-shadow-focus)"})])])]),x("checked",`
 background: var(--n-button-color-active);
 color: var(--n-button-text-color-active);
 border-color: var(--n-button-border-color-active);
 `),x("disabled",`
 cursor: not-allowed;
 opacity: var(--n-opacity-disabled);
 `)])]);function xe(o,e,t){var a;const r=[];let l=!1;for(let d=0;d<o.length;++d){const c=o[d],i=(a=c.type)===null||a===void 0?void 0:a.name;i==="RadioButton"&&(l=!0);const f=c.props;if(i!=="RadioButton"){r.push(c);continue}if(d===0)r.push(c);else{const g=r[r.length-1].props,C=e===g.value,h=g.disabled,R=e===f.value,m=f.disabled,w=(C?2:0)+(h?0:1),z=(R?2:0)+(m?0:1),k={[`${t}-radio-group__splitor--disabled`]:h,[`${t}-radio-group__splitor--checked`]:C},n={[`${t}-radio-group__splitor--disabled`]:m,[`${t}-radio-group__splitor--checked`]:R},u=w<z?n:k;r.push(y("div",{class:[`${t}-radio-group__splitor`,u]}),c)}}return{children:r,isButtonGroup:l}}const Ce=Object.assign(Object.assign({},V.props),{name:String,value:[String,Number,Boolean],defaultValue:{type:[String,Number,Boolean],default:null},size:String,disabled:{type:Boolean,default:void 0},"onUpdate:value":[Function,Array],onUpdateValue:[Function,Array]}),ke=G({name:"RadioGroup",props:Ce,setup(o){const e=F(null),{mergedSizeRef:t,mergedDisabledRef:a,nTriggerFormChange:r,nTriggerFormInput:l,nTriggerFormBlur:d,nTriggerFormFocus:c}=N(o),{mergedClsPrefixRef:i,inlineThemeDisabled:f,mergedRtlRef:g}=j(o),C=V("Radio","-radio-group",me,q,o,i),h=F(o.defaultValue),R=U(o,"value"),m=W(R,h);function w(b){const{onUpdateValue:p,"onUpdate:value":$}=o;p&&I(p,b),$&&I($,b),h.value=b,r(),l()}function z(b){const{value:p}=e;p&&(p.contains(b.relatedTarget)||c())}function k(b){const{value:p}=e;p&&(p.contains(b.relatedTarget)||d())}ce(J,{mergedClsPrefixRef:i,nameRef:U(o,"name"),valueRef:m,disabledRef:a,mergedSizeRef:t,doUpdateValue:w});const n=L("Radio",g,i),u=_(()=>{const{value:b}=t,{common:{cubicBezierEaseInOut:p},self:{buttonBorderColor:$,buttonBorderColorActive:A,buttonBorderRadius:T,buttonBoxShadow:H,buttonBoxShadowFocus:P,buttonBoxShadowHover:Y,buttonColor:Q,buttonColorActive:X,buttonTextColor:Z,buttonTextColorActive:ee,buttonTextColorHover:oe,opacityDisabled:te,[D("buttonHeight",b)]:re,[D("fontSize",b)]:ne}}=C.value;return{"--n-font-size":ne,"--n-bezier":p,"--n-button-border-color":$,"--n-button-border-color-active":A,"--n-button-border-radius":T,"--n-button-box-shadow":H,"--n-button-box-shadow-focus":P,"--n-button-box-shadow-hover":Y,"--n-button-color":Q,"--n-button-color-active":X,"--n-button-text-color":Z,"--n-button-text-color-hover":oe,"--n-button-text-color-active":ee,"--n-height":re,"--n-opacity-disabled":te}}),v=f?K("radio-group",_(()=>t.value[0]),u,o):void 0;return{selfElRef:e,rtlEnabled:n,mergedClsPrefix:i,mergedValue:m,handleFocusout:k,handleFocusin:z,cssVars:f?void 0:u,themeClass:v==null?void 0:v.themeClass,onRender:v==null?void 0:v.onRender}},render(){var o;const{mergedValue:e,mergedClsPrefix:t,handleFocusin:a,handleFocusout:r}=this,{children:l,isButtonGroup:d}=xe(le(ue(this)),e,t);return(o=this.onRender)===null||o===void 0||o.call(this),y("div",{onFocusin:a,onFocusout:r,ref:"selfElRef",class:[`${t}-radio-group`,this.rtlEnabled&&`${t}-radio-group--rtl`,this.themeClass,d&&`${t}-radio-group--button-group`],style:this.cssVars},l)}});export{ke as N,ze as a,q as r};
