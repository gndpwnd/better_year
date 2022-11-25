const fs = require('fs');
const path = require('path');
const webpack = require('webpack');

const MiniCssExtractPlugin = require("mini-css-extract-plugin");

module.exports = {
    entry: {
        'js/drive_code': './js/drive_code.js',
        'js/tasks_code': './js/tasks_code.js',
    },
    output: {
        path: path.resolve(__dirname, 'dist'),
        filename: '[name].bundle.js',
    },
    plugins: [
        new webpack.ProvidePlugin({
            google: 'google',
        }),
        new webpack.DefinePlugin({
            'process.env': {
                EX_OAUTH_CLIENT_ID: JSON.stringify(process.env.EX_OAUTH_CLIENT_ID),
                EX_API_KEY: JSON.stringify(process.env.EX_API_KEY),
            },
        }),
    ],
    module: {
        rules: [
            {
                //Apply rule for .js files
                test: /\.js$/,
                exclude: /(node_modules)/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: ['@babel/preset-env'],
                    },
                },
            },

            {
                // Apply rule for .sass, .scss or .css files
                test: /\.(sa|sc|c)ss$/,
          
                use: [
                    {
                        loader: MiniCssExtractPlugin.loader,
                    },
                    {
                        // This loader resolves url() and @imports inside CSS
                        loader: "css-loader",
                    },
                    {
                        // Then we apply postCSS fixes like autoprefixer and minifying
                        loader: "postcss-loader"
                    },
                    {
                        // First we transform SASS to standard CSS
                        loader: "sass-loader",
                        options: {
                            implementation: require("sass")
                        }
                    }
                    ]
              },

              {
                // Apply rule for images
                test: /\.(png|jpe?g|gif|svg|webp)$/,
                use: [
                       {
                         // Using file-loader for these files
                         loader: "file-loader",
          
                         // In options we can set different things like format
                         // and directory to save
                         options: {
                           outputPath: 'images'
                         }
                       }
                     ]
              },

              {
                // Apply rules for fonts files
                test: /\.(woff|woff2|ttf|otf|eot)$/,
                use: [
                       {
                         // Using file-loader too
                         loader: "file-loader",
                         options: {
                           outputPath: 'fonts'
                         }
                       }
                     ]
              }
        ],
    },
    plugins: [

        new MiniCssExtractPlugin({
            filename: "bundle.css"
        })
    ]

};