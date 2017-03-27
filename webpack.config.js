let path = require('path')
let webpack = require('webpack')
let ExtractTextPlugin = require('extract-text-webpack-plugin')
let OptimizeCssAssetsPlugin = require('optimize-css-assets-webpack-plugin');

let plugins = [
    new ExtractTextPlugin('app.css')
]

if (process.env.NODE_ENV === 'production') {
    plugins.push(
        new webpack.optimize.UglifyJsPlugin(),
        new OptimizeCssAssetsPlugin()
    )
}

module.exports = {
    entry: [
        './resources/js/app.js',
        './resources/sass/app.scss'
    ],
    module: {
        loaders: [{
            test: /\.js$/,
            exclude: /(node_modules|bower_components)/,
            loader: 'babel-loader',
            query: {
                presets: ['es2015']
            }
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
           'jquery': require.resolve('jquery')
        }
    },
    output: {
        filename: 'app.js',
        path: path.resolve(__dirname, 'static')
    },
    plugins
}
