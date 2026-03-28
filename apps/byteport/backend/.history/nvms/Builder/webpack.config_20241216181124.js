import path from "path";
import SpinSdkPlugin from "@fermyon/spin-sdk/plugins/webpack/index.js";
import { fileURLToPath } from "url";
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
export default {
	entry: "./src/spin.ts",
	experiments: {
		outputModule: true,
	},
	module: {
		rules: [
			{
				test: /\.tsx?$/,
				use: "ts-loader",
				exclude: /node_modules/,
			},
		],
	},
	resolve: {
		extensions: [".tsx", ".ts", ".js"],
	},
	output: {
		path: path.resolve(__dirname, "./"),
		filename: "dist.js",
		module: true,
		library: {
			type: "module",
		},
	},
	plugins: [new SpinSdkPlugin()],
	optimization: {
		minimize: false,
	},
};
