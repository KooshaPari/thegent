import path from "path";
import SpinSdkPlugin from "@fermyon/spin-sdk/plugins/webpack/index.js";

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
