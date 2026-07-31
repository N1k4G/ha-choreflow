import typescript from "@rollup/plugin-typescript";
import resolve from "@rollup/plugin-node-resolve";
import commonjs from "@rollup/plugin-commonjs";
import terser from "@rollup/plugin-terser";

const dev = process.env.ROLLUP_WATCH;
const thirdPartyBanner = `/*!
 * ChoreFlow card third-party notices:
 * lit — Copyright (c) 2017 Google LLC — BSD-3-Clause
 * custom-card-helpers — Copyright (c) 2019 Custom cards for Home Assistant — MIT
 * Full license texts: https://github.com/N1k4G/ha-choreflow/blob/main/THIRD_PARTY_NOTICES.md
 */`;

export default {
  input: "src/choreflow-card.ts",
  output: {
    file: "dist/choreflow-card.js",
    format: "es",
    sourcemap: dev ? true : false,
    inlineDynamicImports: true,
    banner: thirdPartyBanner,
  },
  plugins: [
    resolve(),
    commonjs(),
    typescript({ tsconfig: "./tsconfig.json" }),
    !dev && terser({ format: { comments: /^!/ } }),
  ],
};
