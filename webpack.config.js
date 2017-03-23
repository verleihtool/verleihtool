var path = require('path'),
    ExtractTextPlugin = require('extract-text-webpack-plugin');

module.exports = {
    entry: [
        './resources/js/app.js',
        './resources/sass/app.scss'
    ],
    module: {
        loaders: [{
            test: /\.js$/,
            loader: 'babel-loader'
        }, {
            test: /\.scss$/,
            loader: ExtractTextPlugin.extract({
                fallback: 'style-loader',
                use: 'css-loader?sourceMap!sass-loader?sourceMap'
            })
        }, {
            test: /\.(woff2?|ttf|eot|svg|otf)$/,
            loader: 'file-loader'
        }]
    },
    resolve: {
        alias: {
           'jquery': require.resolve('jquery'),
        }
    },
    output: {
        filename: 'app.js',
        path: path.resolve(__dirname, 'static')
    },
    plugins: [
        new ExtractTextPlugin('app.css')
    ]
};
