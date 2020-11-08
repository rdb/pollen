#version 330

uniform mat4 p3d_ModelMatrix;
uniform mat4 p3d_ViewMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform mat4 p3d_ProjectionMatrix;

in vec4 p3d_Vertex;
in vec4 p3d_Tangent;
in vec2 p3d_MultiTexCoord0;

uniform float osg_FrameTime;

uniform vec3 player;
uniform vec3 scale;
uniform sampler2D terrainmap;
uniform sampler2D windmap;
uniform sampler2D satmap;

out vec3 v_position;
out vec4 v_color;
out vec3 v_normal;
out vec2 v_texcoord;

void main() {
    mat4 modelmat = p3d_ModelMatrix;
    modelmat[3][2] = 0;
    vec3 wspos = (modelmat * p3d_Vertex).xyz;

    // normal is stored in xyz, height in alpha
    vec4 sample = texture(terrainmap, wspos.xy * scale.xy);
    float hval = sample.a;
    vec3 normal = sample.xyz * 2.0 - 1.0;

    float t = p3d_MultiTexCoord0.y;
    float wind = texture(windmap, wspos.xy * scale.xy * 4 + vec2(osg_FrameTime * 0.06, 0)).r - 0.5;
    float wind_offset = wind * (t * t) * 5;

    v_color.g = hval * 0.333;
    v_color.a = 1;

    float sat = texture(satmap, wspos.xy * scale.xy).r;
    v_color.b = (sat > 0.5) ? 1.0 : sat*2;

    vec2 shove = vec2(0);
    float factor = 0;

    vec2 delta = wspos.xy - player.xy;

    //delta *= (p3d_ViewMatrix * vec4(0.13, 0, 0, 0)).xy;
    //delta *= (1.0 - dot(normalize(delta), normalize(-playerdir.xy))) * 1;

    //delta.y *= 0.13;
    float dist = length(delta);
    if (dist < 3) {
        delta = normalize(delta);
        shove = delta * ((t * t) * (3 - dist) / 3) * 2;
        factor = (1.0 - (dist / 3)) * player.z;

        // Hide grass too close to player
        if (dist < 2) {
            v_color.a = mix(1, dist * 0.8, player.z);
        }
    }

    wspos.xy += v_color.b * mix(vec2(wind_offset, 0), shove, factor);
    normal.x += v_color.b * mix(wind_offset * 0.8, 0, factor);

    wspos.z *= (0.5 + v_color.b * 0.5);

    //wspos.x += wind_offset;
    //normal.x += wind_offset * 0.8;

    wspos.z += hval * scale.z;

    v_position = vec3(p3d_ViewMatrix * vec4(wspos, 1));
    v_normal = normalize((p3d_ViewMatrix * vec4(normal, 0)).xyz);
    v_texcoord = p3d_MultiTexCoord0;
    gl_Position = p3d_ProjectionMatrix * vec4(v_position, 1);

    v_color.r = t;
}
