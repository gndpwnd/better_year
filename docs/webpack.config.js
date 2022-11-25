const fs = require('fs');
const path = require('path');
const webpack = require('webpack');

module.exports = (env) => {

    //const EX_OAUTH_CLIENT_ID = env === 'EX_OAUTH_CLIENT_ID';
    //const EX_API_KEY = env === 'EX_API_KEY';
    //const SUM = env === 'SUM';
    //get the environment variables

    const EX_OAUTH_CLIENT_ID = JSON.stringify(JSON.stringify(process.env.EX_OAUTH_CLIENT_ID));
    const EX_API_KEY = JSON.stringify(JSON.stringify(process.env.EX_API_KEY));
    var SUM = JSON.stringify(process.env.SUM);


//    console.log('EX_OAUTH_CLIENT_ID', EX_OAUTH_CLIENT_ID);
//    console.log('EX_API_KEY', EX_API_KEY);
//    console.log('SUM', SUM);

    return {
        entry: {
            'js/tasks_code': './js/tasks_code.js',
            'js/drive_code': './js/drive_code.js',
        },
        output: {
            path: path.resolve(__dirname, 'dist'),
            filename: '[name].mod.js',
        },
        plugins: [
            new webpack.DefinePlugin({
                EX_OAUTH_CLIENT_ID,
                EX_API_KEY,
                SUM,
            }),
        ],
        // loader
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