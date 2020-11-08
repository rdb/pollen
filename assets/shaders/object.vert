#version 330

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform mat3 p3d_NormalMatrix;

in vec4 p3d_Vertex;
in vec4 p3d_Color;
in vec3 p3d_Normal;
in vec2 p3d_MultiTexCoord0;

out vec3 v_position;
out vec4 v_color;
out vec2 v_texcoord;
out vec3 v_normal;

void main() {
    v_position = vec3(p3d_ModelViewMatrix * p3d_Vertex);
    v_color = p3d_Color;
    v_normal = normalize(p3d_NormalMatrix * p3d_Normal);
    v_texcoord = p3d_MultiTexCoord0;

    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
}
