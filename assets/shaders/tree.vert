#version 120

uniform mat4 p3d_ProjectionMatrix;
uniform mat4 p3d_ModelMatrix;
uniform mat4 p3d_ViewMatrix;
uniform mat3 p3d_NormalMatrix;

uniform vec3 scale;
uniform sampler2D windmap;
uniform sampler2D satmap;

uniform float osg_FrameTime;

attribute vec4 p3d_Vertex;
attribute vec4 p3d_Color;
attribute vec3 p3d_Normal;
attribute vec2 p3d_MultiTexCoord0;

varying vec3 v_position;
varying vec4 v_color;
varying vec2 v_texcoord;
varying vec3 v_normal;

void main() {
    vec3 wspos = (p3d_ModelMatrix * p3d_Vertex).xyz;

    float t = p3d_Vertex.z / 5;

    float wind = texture2D(windmap, wspos.xy * scale.xy * 4 + vec2(osg_FrameTime * 0.06, 0)).r - 0.5;
    float wind_offset = wind * t * t;
    wspos.x += wind_offset;

    v_position = vec3(p3d_ViewMatrix * vec4(wspos, 1));
    v_color = p3d_Color;
    v_normal = normalize(p3d_NormalMatrix * p3d_Normal);
    v_texcoord = p3d_MultiTexCoord0;

    float sat = texture2D(satmap, wspos.xy * scale.xy).r;
    v_color.rgb = mix(v_color.ggg, v_color.rgb, (sat > 0.5) ? 1.0 : sat*2);

    gl_Position = p3d_ProjectionMatrix * vec4(v_position, 1);
}
