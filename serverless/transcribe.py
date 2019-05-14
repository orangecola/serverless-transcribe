import boto3

def main(event, context):
    bucketName=event["Records"][0]["s3"]["bucket"]["name"]
    key=event["Records"][0]["s3"]["object"]["key"]
    mediaUri = "https://" + bucketName + ".s3.amazonaws.com/" + key 
    transcribe = boto3.client('transcribe')
    response = transcribe.start_transcription_job(
        TranscriptionJobName=key.split(".")[0],
        LanguageCode='en-US',
        MediaFormat='mp3',
        Media={
            'MediaFileUri': mediaUri
        },
        OutputBucketName=bucketName,
        Settings={
        'ShowSpeakerLabels': True,
        'MaxSpeakerLabels': 2,
        }
    )
    print(response)