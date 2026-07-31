import typescript from "@rollup/plugin-typescript";
import resolve from "@rollup/plugin-node-resolve";
import commonjs from "@rollup/plugin-commonjs";
import terser from "@rollup/plugin-terser";
import { readFileSync } from "node:fs";

const dev = process.env.ROLLUP_WATCH;
const thirdPartyNotices = readFileSync(
  new URL("../THIRD_PARTY_NOTICES.md", import.meta.url),
  "utf8",
).trimEnd();
const thirdPartyBanner = `/*!\n${thirdPartyNotices}\n*/`;

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
