// Fragment shader

#version 400

// Interpolated values from geometry shader
in vec2 uv_gs;
in vec3 normal_gs;
in vec3 eye_gs;
in vec3 light_gs;

// Ouput data
out vec4 color_out;

// Uniform values that stay constant for the whole mesh
uniform mat4 MVP;
uniform sampler2D waterTexture;

void phongColor() {

    // Light emission properties
    vec4 LightColor = vec4(1,1,1,1);

    // Material properties
    vec4 MaterialDiffuseColor = texture(waterTexture, uv_gs);  // Color of the water
    vec4 MaterialAmbientColor = vec4(0.2,0.2,0.2,1.0) * MaterialDiffuseColor;  // Simulates indirect lighting
    vec4 MaterialSpecularColor = vec4(0.7, 0.7, 0.7,1.0);  // Reflection highlights

    // Compute color
    vec3 n = normalize(normal_gs);
    vec3 l = normalize(light_gs);
    float cosTheta = clamp( dot( n,l ), 0,1 );

    vec3 E = normalize(eye_gs);
    vec3 R = reflect(-l,n);
    float cosAlpha = clamp( dot( E,R ), 0,1 );

    color_out = MaterialAmbientColor + MaterialDiffuseColor * LightColor * cosTheta + MaterialSpecularColor * LightColor * pow(cosAlpha,2);
}

void main(){
    phongColor();
}