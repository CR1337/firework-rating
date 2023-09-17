import axios from 'axios';

export function getVideoIdFromUrl(urlStream) {
    let regExp = /^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.?be)(\/)?(watch\?v=|\?v=)?(.*)$/;
    let match = urlStream.match(regExp);
    return (match && match[6].length === 11) ? match[6] : null;
}

function extractMimeType(mimeTypeText) {
    const mimeTypeMatch = mimeTypeText.match(/^[^;]+/);
    return mimeTypeMatch ? mimeTypeMatch[0] : "video/webm";
}

export async function getYtVideo(id, host = 'localhost', port = 5624) {
    const url = `http://${host}:${port}/?id=${id}`;
    let ytVideoData = {};

    return axios.get(url)
        .then((res) => {
            const responseData = res.data;
            if (!responseData.success) {
                console.error(`Error getting video data. Status Code: ${responseData.data.statusCode}`);
            }

            const playerResponse = responseData.data.player_response;
            if (!playerResponse.playabilityStatus.playableInEmbed) {
                console.error('This video cannot be played natively!');
            }

            const streamingData = playerResponse.streamingData;
            const allFormats = [...streamingData.formats, ...streamingData.adaptiveFormats];
            
            const videoFormats = allFormats.filter(format => format.mimeType.startsWith("video/"));
            const audioFormats = allFormats.filter(format => format.mimeType.startsWith("audio/"));

            videoFormats.sort((a, b) => {
                if (a.width === b.width) {
                    return b.bitrate - a.bitrate;
                }
                return b.width - a.width;
            });
            
            audioFormats.sort((a, b) =>{
                return b.bitrate - a.bitrate;
            })
            
            ytVideoData.videoUrl = videoFormats[0].url;
            ytVideoData.mimeType = extractMimeType(videoFormats[0].mimeType);
            ytVideoData.audioUrl = audioFormats[0].url;
            return ytVideoData;
        }).catch((error) => {
            console.error(error.message || "Error fetching video data.");
        });
}
