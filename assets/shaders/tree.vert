#version 330

uniform mat4 p3d_ProjectionMatrix;
uniform mat4 p3d_ModelMatrix;
uniform mat4 p3d_ViewMatrix;
uniform mat3 p3d_NormalMatrix;

uniform vec3 scale;
uniform sampler2D windmap;
uniform sampler2D satmap;

uniform float osg_FrameTime;

in vec4 p3d_Vertex;
in vec4 p3d_Color;
in vec3 p3d_Normal;

out vec3 v_position;
out vec4 v_color;
out vec2 v_texcoord;
out vec3 v_normal;

void main() {
    vec3 wspos_model = p3d_ModelMatrix[3].xyz;
    vec3 wspos = (p3d_ModelMatrix * p3d_Vertex).xyz;

    float sat = texture(satmap, wspos_model.xy * scale.xy).r;
    sat = (sat > 0.5) ? 1.0 : sat*2;

    v_color.a = 1;

    if (p3d_Color.g > 0.7) {
      v_color.a = sat + 0.25 - mod(wspos.x + wspos.y * 10 + wspos.z * 100, 0.5);
    }


    float t = p3d_Vertex.z / 5;

    float wind = texture(windmap, wspos.xy * scale.xy * 4 + vec2(osg_FrameTime * 0.06, 0)).r - 0.5;
    float wind_offset = wind * t * t;
    wspos.x += wind_offset;

    v_position = vec3(p3d_ViewMatrix * vec4(wspos, 1));
    v_normal = normalize(p3d_NormalMatrix * p3d_Normal);
    v_texcoord = vec2(0, 0);

    v_color.rgb = p3d_Color.rgb;
    v_color.rgb = mix(v_color.ggg * vec3(188/255.0, 152/255.0, 101/255.0), v_color.rgb, sat);


    gl_Position = p3d_ProjectionMatrix * vec4(v_position, 1);
}
