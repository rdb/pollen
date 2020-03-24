#version 120

uniform mat4 p3d_ModelMatrix;
uniform mat4 p3d_ViewMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform mat4 p3d_ProjectionMatrix;

attribute vec4 p3d_Vertex;
attribute vec4 p3d_Tangent;
attribute vec2 p3d_MultiTexCoord0;

uniform float osg_FrameTime;

uniform vec2 player;
uniform vec3 scale;
uniform sampler2D terrainmap;
uniform sampler2D windmap;

varying vec3 v_position;
varying vec4 v_color;
varying vec3 v_normal;
varying vec2 v_texcoord;

void main() {
    vec3 wspos = (p3d_ModelMatrix * p3d_Vertex).xyz;

    // normal is stored in xyz, height in alpha
    vec4 sample = texture2D(terrainmap, wspos.xy * scale.xy);
    float hval = sample.a;
    vec3 normal = sample.xyz * 2.0 - 1.0;

    float t = p3d_MultiTexCoord0.y;
    float wind = texture2D(windmap, wspos.xy * scale.xy * 4 + vec2(osg_FrameTime * 0.06, 0)).r - 0.5;
    float wind_offset = wind * (t * t) * 5;

    v_color.r = min(1.0, t * 1.5);
    v_color.g = hval;
    v_color.a = 1;

    vec2 delta = wspos.xy - player;
    delta.y *= 0.13;
    float dist = length(delta);
    if (dist < 2.5) {
        delta = normalize(delta);
        wspos.xy += delta * ((t * t) * ((3 - (dist - 0.75)) / 1.5));
        wspos.x += wind_offset * (dist / 3);

        // Hide grass too close to player
        if (dist < 0.75) {
            v_color.a = dist / 0.75;
        }
    } else {
        wspos.x += wind_offset;
        normal.x += wind_offset * 0.8;
    }

    wspos.z += hval * scale.z;

    v_position = vec3(p3d_ViewMatrix * vec4(wspos, 1));
    v_normal = normalize((p3d_ViewMatrix * vec4(normal, 0)).xyz);
    v_texcoord = p3d_MultiTexCoord0;
    gl_Position = p3d_ProjectionMatrix * vec4(v_position, 1);
}
