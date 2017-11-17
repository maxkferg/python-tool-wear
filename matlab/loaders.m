
function loadAudio(self,tool,folder)
    % Load the raw audio data
    delimeter = ' ';
    filepath = sprintf('%s/audio_T%02i*',folder,tool);
    files = dir(filepath);
    if isempty(files)
        error('No audio files matching %s found',filepath)
    end
    for i = 1:length(files)
        filepath = sprintf('%s/%s', folder, files(i).name);
        fprintf('Reading audio file %s\n',filepath);
        self.convertUTF8(filepath);
        % Parse the data ignoring time stamps
        fid = fopen(filepath);
        parsed = textscan(fid,'%f','commentStyle','2016-','delimiter',delimeter,'headerLines',1);
        partdata = parsed{1};
        fclose(fid);
        % Store the start point, and part data
        self.audioDelimeters(end+1) = length(self.audioTimeSeries)+1;
        self.audioTimeSeries = vertcat(self.audioTimeSeries, partdata);
    end
end

function loadVibration(self,tool,folder)
    % Load the vibration data
    delimeter = ' ';
    filepath = sprintf('%s/accel_T%02i*',folder,tool);
    files = dir(filepath);
    if isempty(files)
        error('No acceleration files matching %s found',filepath)
    end
    for i = 1:length(files)
        filepath = sprintf('%s/%s', folder, files(i).name);
        fprintf('Reading vibration file %s\n',filepath);
        self.convertUTF8(filepath);
        % Parse the data ignoring time stamps
        fid = fopen(filepath);
        parsed = textscan(fid,'%f %f %f','commentStyle','2016-','delimiter',delimeter,'headerLines', 1); 
        p1 = parsed{1};
        p2 = parsed{2};
        p3 = parsed{3};
        height = min([length(p1) length(p2) length(p3)]);
        partdata = [p1(1:height) p2(1:height) p3(1:height)];
        fclose(fid);
        % Store the start point, and part data
        self.vibrationDelimeters(end+1) = length(self.vibrationTimeSeries)+1;
        self.vibrationTimeSeries = vertcat(self.vibrationTimeSeries, partdata);
    end
end