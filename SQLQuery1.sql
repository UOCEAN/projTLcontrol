use AwxLogger
select EventTime, ActiveTime, CV, Source, Message, LastCmdBy from dbo.TL_AlarmLogger 
order by EventTime desc 