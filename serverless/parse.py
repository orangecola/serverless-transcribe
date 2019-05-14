import json, boto3

def main(event, context):
    bucketName=event["Records"][0]["s3"]["bucket"]["name"]
    key=event["Records"][0]["s3"]["object"]["key"]
    local_json = '/tmp/' + key
    outputKey = key.split('.')[0] + '.txt'
    local_output = '/tmp/' + outputKey
    
    s3 = boto3.client('s3')
    s3.download_file(bucketName, key, local_json)
    with open(local_json) as read_file:
        data = json.load(read_file)
        labels = data["results"]["speaker_labels"]["segments"]
        speaker_start_times = {}

        #Speaker labels
        for label in labels:
            for item in label["items"]:
                speaker_start_times[item["start_time"]] = item["speaker_label"]
        
        items = data["results"]["items"]
        lines = []
        line = ''
        time = 0
        speaker = None
        for item in items:
            content = item["alternatives"][0]["content"]
            if "start_time" in item:
                current_speaker = speaker_start_times[item["start_time"]]
            elif item["type"] == "punctuation":
                line += content
            if current_speaker != speaker:
                if speaker != None:
                    lines.append(
                        {
                            "speaker": speaker,
                            "line": line,
                            "time": time
                        }
                    )
                line = content
                speaker = current_speaker
                time = item["start_time"]
                
            elif item["type"] != "punctuation":
                line += ' ' + content
        lines.append(
            {
                "speaker": speaker,
                "line": line,
                "time": time
            }
        )
    with open(local_output, "w") as write_file:
        for line in lines:
            write_file.write('[' + line["time"] + ']' + line["speaker"] + ': ' + line["line"])
            write_file.write('\n')
    s3.upload_file(local_output, bucketName, outputKey)