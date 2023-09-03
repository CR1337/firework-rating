import axios from 'axios';

export function getVideoIdFromUrl(urlStream) {
    let regExp = /^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.?be)(\/)?(watch\?v=|\?v=)?(.*)$/;
    let match = urlStream.match(regExp);
    return (match && match[6].length === 11) ? match[6] : null;
}

export async function getBestUrl(id, host = 'localhost', port = 5624) {
    const url = `http://${host}:${port}/?id=${id}`;
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

            allFormats.sort((a, b) => {
                if (a.width === b.width) {
                    return b.bitrate - a.bitrate;
                }
                return b.width - a.width;
            });

            return allFormats[0].url;
        }).catch((error) => {
            console.error(error.message || "Error fetching video data.");
        });
}
