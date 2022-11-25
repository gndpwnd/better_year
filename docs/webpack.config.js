const fs = require('fs');
const path = require('path');
const webpack = require('webpack');

module.exports = (env) => {

    const EX_OAUTH_CLIENT_ID = JSON.stringify(process.env.EX_OAUTH_CLIENT_ID);
    const EX_API_KEY = JSON.stringify(process.env.EX_API_KEY);

    return {

        entry: {
            'env_vars': './js-templates/env_vars.js',
        },

        output: {
            path: path.resolve(__dirname, 'modules'),
            filename: '[name].mod.js',
        },

        plugins: [
            new webpack.DefinePlugin({
                EX_OAUTH_CLIENT_ID,
                EX_API_KEY,
            }),
        ],

        module: {
            rules: [
                {
                    test: /\.js$/,
                    exclude: /node_modules/,
                    use: {
                        loader: 'babel-loader',
                        options: {
                            presets: ['@babel/preset-env'],
                        },
                    },
                },
            ],
        },
    };

};